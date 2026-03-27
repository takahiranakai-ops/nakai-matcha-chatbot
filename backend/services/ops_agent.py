"""Claude tool-use agent for NAKAI operations chat.

Natural language → tool calls → results → natural language response.
"""

import json
import logging
from typing import AsyncGenerator

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are NAKAI Operations Assistant — an AI that manages the NAKAI Matcha business systems.

You have access to tools for B2B sales, email marketing, social content, analytics, and market research.
When the user asks you to do something, use the appropriate tool. Always respond in the same language the user uses.

Guidelines:
- Be concise and action-oriented
- When showing data, format it clearly with numbers and key metrics
- If a tool returns an error, explain what happened and suggest alternatives
- For destructive actions (delete, send emails), confirm what you're about to do
- Use Japanese when the user writes in Japanese, English otherwise
"""

TOOLS = [
    {
        "name": "get_b2b_stats",
        "description": "Get B2B sales dashboard statistics (total leads, open/won, outreach sent, reply rate).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "search_leads",
        "description": "Search B2B leads by region, status, segment, or free text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Filter by region (e.g. 'Portland', 'Tokyo')"},
                "status": {"type": "string", "description": "Filter by status: new/contacted/replied/qualified/won/lost"},
                "segment": {"type": "string", "description": "Filter by segment: cafe/hotel/restaurant/retail/online"},
                "search": {"type": "string", "description": "Free text search in company name/email"},
                "limit": {"type": "integer", "description": "Max results (default 20)", "default": 20},
            },
            "required": [],
        },
    },
    {
        "name": "update_lead_status",
        "description": "Update a B2B lead's status or notes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "string", "description": "UUID of the lead"},
                "status": {"type": "string", "description": "New status: new/contacted/replied/qualified/won/lost"},
                "notes": {"type": "string", "description": "Notes to add"},
            },
            "required": ["lead_id"],
        },
    },
    {
        "name": "discover_leads",
        "description": "Discover new B2B leads via Google Places in a given city/region and segment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Region for discovery (e.g. 'US-West')"},
                "city": {"type": "string", "description": "City name (e.g. 'Portland')"},
                "segment": {"type": "string", "description": "Business type: cafe/hotel/restaurant/retail"},
            },
            "required": ["city", "segment"],
        },
    },
    {
        "name": "run_b2b_pipeline",
        "description": "Run the daily B2B outreach pipeline (sends emails to qualified leads).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "preview_today_content",
        "description": "Preview today's AI-generated social media content (Twitter, Reddit, Threads, etc.).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "force_post_content",
        "description": "Force-post today's content to all social platforms immediately.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_posting_history",
        "description": "Get recent social media posting history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of recent posts (default 15)", "default": 15},
            },
            "required": [],
        },
    },
    {
        "name": "list_email_campaigns",
        "description": "List email marketing campaigns.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "create_email_campaign",
        "description": "Create a new AI-designed email campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Campaign name"},
                "description": {"type": "string", "description": "What the email should be about"},
            },
            "required": ["name", "description"],
        },
    },
    {
        "name": "list_subscribers",
        "description": "List email subscribers, optionally filtered by tag or language.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Filter by tag (e.g. 'wholesale', 'newsletter')"},
                "language": {"type": "string", "description": "Filter by language ('en' or 'ja')"},
            },
            "required": [],
        },
    },
    {
        "name": "sync_shopify_subscribers",
        "description": "Sync Shopify customers into the email subscriber list.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "reingest_knowledge",
        "description": "Re-ingest knowledge base into the chatbot's vector store.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_chat_analytics",
        "description": "Get chatbot analytics (total conversations, messages, popular topics).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_shopify_stats",
        "description": "Get Shopify store statistics (products, orders, revenue).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_research_brief",
        "description": "Get the latest market research findings (competitor watch, market trends, B2B intel).",
        "input_schema": {
            "type": "object",
            "properties": {
                "research_type": {
                    "type": "string",
                    "description": "Type: market_intel/competitor_watch/b2b_intel/content_gaps (default: all)",
                },
                "days": {"type": "integer", "description": "Look back N days (default 7)", "default": 7},
            },
            "required": [],
        },
    },
]


async def _execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return the result as a JSON string."""
    try:
        if name == "get_b2b_stats":
            from services.b2b.analytics import get_dashboard_stats
            result = await get_dashboard_stats()

        elif name == "search_leads":
            result = await _search_b2b_leads(args)

        elif name == "update_lead_status":
            result = await _update_b2b_lead(args)

        elif name == "discover_leads":
            from services.b2b.lead_researcher import search_leads_in_city
            found = await search_leads_in_city(
                city=args["city"],
                segment=args.get("segment", "cafe"),
                region=args.get("region", ""),
            )
            result = {"found": found, "city": args["city"], "segment": args.get("segment", "cafe")}

        elif name == "run_b2b_pipeline":
            from services.b2b.pipeline import run_daily_pipeline
            result = await run_daily_pipeline()

        elif name == "preview_today_content":
            from services.daily_content import generate_daily_tips
            content = await generate_daily_tips()
            result = {"preview": True, "content": content}

        elif name == "force_post_content":
            from services.daily_content import generate_daily_tips
            from services.social_poster import post_all
            content = await generate_daily_tips()
            results = await post_all(content)
            result = {"posted": True, "results": results}

        elif name == "get_posting_history":
            result = await _get_posting_history(args.get("limit", 15))

        elif name == "list_email_campaigns":
            result = await supabase_client.list_email_campaigns()

        elif name == "create_email_campaign":
            from services.email_ai import generate_email_design
            brand_assets = await supabase_client.get_email_brand_assets()
            html = await generate_email_design(
                description=args["description"],
                brand_assets=brand_assets or {},
            )
            campaign = await supabase_client.create_email_campaign({
                "name": args["name"],
                "description": args["description"],
                "html_content": html,
                "status": "draft",
            })
            result = {"created": True, "campaign": campaign}

        elif name == "list_subscribers":
            result = await supabase_client.list_email_subscribers(
                tag=args.get("tag"),
                language=args.get("language"),
            )

        elif name == "sync_shopify_subscribers":
            from services.shopify_client import get_customers
            customers = await get_customers()
            synced = 0
            for c in customers:
                email = c.get("email")
                if not email:
                    continue
                await supabase_client.create_email_subscriber(
                    email=email,
                    name=c.get("first_name", ""),
                    tags=["shopify"],
                    language="en",
                )
                synced += 1
            result = {"synced": synced, "total_shopify": len(customers)}

        elif name == "reingest_knowledge":
            import asyncio
            import api.routes as routes_module
            if routes_module._refresh_running:
                result = {"status": "already_running"}
            else:
                routes_module._refresh_running = True
                asyncio.create_task(routes_module._run_ingestion_background())
                result = {"status": "started"}

        elif name == "get_chat_analytics":
            result = await supabase_client.get_analytics_summary()

        elif name == "get_shopify_stats":
            from services.shopify_client import get_products
            products = await get_products()
            result = {"total_products": len(products), "products": [p.get("title") for p in products[:10]]}

        elif name == "get_research_brief":
            result = await _get_research_brief(
                research_type=args.get("research_type"),
                days=args.get("days", 7),
            )

        else:
            result = {"error": f"Unknown tool: {name}"}

        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"Tool execution failed [{name}]: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def _supabase_get(table: str, params: dict) -> list:
    """Direct Supabase REST query helper."""
    supabase_client._init()
    client = supabase_client._get_client()
    resp = await client.get(
        f"{supabase_client._BASE_URL}/{table}",
        headers=supabase_client._HEADERS,
        params=params,
    )
    resp.raise_for_status()
    return resp.json()


async def _supabase_patch(table: str, row_id: str, data: dict) -> dict:
    """Direct Supabase REST patch helper."""
    supabase_client._init()
    client = supabase_client._get_client()
    resp = await client.patch(
        f"{supabase_client._BASE_URL}/{table}",
        headers=supabase_client._HEADERS,
        params={"id": f"eq.{row_id}"},
        json=data,
    )
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if rows else {}


async def _search_b2b_leads(args: dict) -> dict:
    """Search B2B leads with filters."""
    params = {
        "select": "id,company_name,email,city,region,status,segment,lead_score,created_at",
        "order": "created_at.desc",
        "limit": str(args.get("limit", 20)),
    }
    if args.get("region"):
        params["region"] = f"ilike.%{args['region']}%"
    if args.get("status"):
        params["status"] = f"eq.{args['status']}"
    if args.get("segment"):
        params["segment"] = f"eq.{args['segment']}"
    if args.get("search"):
        params["or"] = f"(company_name.ilike.%{args['search']}%,email.ilike.%{args['search']}%)"
    try:
        rows = await _supabase_get("b2b_leads", params)
        return {"leads": rows, "total": len(rows)}
    except Exception as e:
        return {"leads": [], "error": str(e)}


async def _update_b2b_lead(args: dict) -> dict:
    """Update a B2B lead's status/notes."""
    updates = {}
    if args.get("status"):
        updates["status"] = args["status"]
    if args.get("notes"):
        updates["notes"] = args["notes"]
    if not updates:
        return {"error": "No fields to update"}
    try:
        return await _supabase_patch("b2b_leads", args["lead_id"], updates)
    except Exception as e:
        return {"error": str(e)}


async def _get_posting_history(limit: int = 15) -> dict:
    """Get recent posting history from daily_tips_log."""
    try:
        rows = await _supabase_get("daily_tips_log", {
            "select": "*",
            "order": "posted_at.desc",
            "limit": str(limit),
        })
        return {"history": rows}
    except Exception as e:
        return {"history": [], "error": str(e)}


async def _get_research_brief(research_type: str | None = None, days: int = 7) -> dict:
    """Fetch market intelligence from Supabase."""
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    params = {"created_at": f"gte.{cutoff}", "order": "created_at.desc", "limit": "20"}
    if research_type:
        params["research_type"] = f"eq.{research_type}"

    try:
        rows = await _supabase_get("market_intelligence", params)
        return {"findings": rows, "count": len(rows), "days": days}
    except Exception:
        return {"findings": [], "count": 0, "note": "No research data yet. Run the research agent first."}


async def run_ops_chat(
    message: str,
    history: list[dict] | None = None,
) -> AsyncGenerator[dict, None]:
    """Run the ops chat agent. Yields events as dicts.

    Event types:
        {"type": "text", "content": "..."}
        {"type": "tool_use", "name": "...", "args": {...}}
        {"type": "tool_result", "name": "...", "result": "..."}
        {"type": "done", "response": "...", "messages": [...]}
    """
    if not settings.anthropic_api_key:
        yield {"type": "done", "response": "Anthropic API key not configured.", "messages": []}
        return

    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    messages = list(history or [])
    messages.append({"role": "user", "content": message})

    max_iterations = 8

    for _ in range(max_iterations):
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            yield {"type": "done", "response": f"API error: {e}", "messages": messages}
            return

        # Process response content blocks
        assistant_content = response.content
        text_parts = []

        for block in assistant_content:
            if block.type == "text":
                text_parts.append(block.text)
                yield {"type": "text", "content": block.text}

        # Add assistant message to history
        messages.append({"role": "assistant", "content": assistant_content})

        # If no tool use, we're done
        if response.stop_reason != "tool_use":
            final_text = "\n".join(text_parts)
            yield {"type": "done", "response": final_text, "messages": messages}
            return

        # Execute tool calls
        tool_results = []
        for block in assistant_content:
            if block.type == "tool_use":
                yield {"type": "tool_use", "name": block.name, "args": block.input}

                result_str = await _execute_tool(block.name, block.input)

                yield {"type": "tool_result", "name": block.name, "result": result_str}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

        messages.append({"role": "user", "content": tool_results})

    # Max iterations reached
    yield {"type": "done", "response": "Reached maximum tool call iterations.", "messages": messages}
