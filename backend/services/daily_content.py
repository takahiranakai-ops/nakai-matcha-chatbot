"""Daily AI Tips content generator — auto-creates platform-optimized posts."""

import logging
from datetime import datetime, timezone

from config import settings

logger = logging.getLogger(__name__)

# 365-day topic rotation (50 categories × ~7 variations each)
TOPIC_CATEGORIES = [
    "メール作成の時短術",
    "議事録の自動化",
    "企画書をAIと作る方法",
    "AIで文章を要約するコツ",
    "プレゼン資料の構成術",
    "報告書を一瞬で作るテクニック",
    "クレーム対応メールの書き方",
    "AIでアイデア出し100個",
    "競合分析をAIにやらせる方法",
    "面接の質問リストを自動生成",
    "部下の評価コメントをAIと書く",
    "SNS投稿のネタ出し術",
    "英語メールをAIに翻訳させるコツ",
    "スピーチ原稿をAIに作らせる",
    "データ分析結果を言葉で説明させる",
    "SWOT分析をAIと30分で完成",
    "お断りメールの角が立たない書き方",
    "AIに催促メールを書かせるテクニック",
    "会議のアジェンダを自動作成",
    "業界ニュースをAIに毎朝まとめさせる",
    "AIプロンプトの基本ルール3つ",
    "ChatGPTとClaudeの使い分け方",
    "無料で使えるAIツールベスト5",
    "AIに長い文章を読ませるコツ",
    "AIの回答精度を上げる一言",
    "表やグラフをAIに作らせる方法",
    "AIでExcel作業を半分にする",
    "研修プログラムをAIで設計",
    "新規事業のアイデアをAIに聞く",
    "顧客の声をAIで分析する方法",
    "AIにビジネス文書の添削をさせる",
    "契約書のチェックポイントをAIに聞く",
    "AIで日報を3分で書く方法",
    "出張報告書を箇条書きから自動生成",
    "採用文をAIで魅力的に書き換える",
    "AIにFAQを作らせる方法",
    "見積書の添え状を瞬時に作成",
    "AIで商品説明文を書くコツ",
    "社内マニュアルをAIで整理する",
    "AIを使った読書メモの取り方",
    "AIに自分の文章のクセを教えてもらう",
    "会議の論点整理をAIにやらせる",
    "AIで翻訳する時の注意点3つ",
    "AIに自社の強みを分析させる方法",
    "プロンプトに「役割」を与える効果",
    "AIの出力を改善する「具体例を見せる」技",
    "AIで週報を自動生成する仕組み",
    "AIにリスク分析をさせるプロンプト",
    "50代がAIを始めるベストな第一歩",
    "AIは敵じゃない、最強の部下だ",
]

SYSTEM_PROMPT = """あなたは「AI活用の先生」です。
50代のビジネスパーソン（経営者・管理職・個人事業主）に、
AIの活用方法を「子供でも理解できるくらい簡単に」教えます。

ルール:
- 難しいカタカナ用語は使わない（使う場合は必ず日本語で補足）
- 「コピペするだけ」で使える具体的なテンプレートを1つ必ず含める
- 温かく優しいトーンで、決して偉そうにしない
- 「今日から5分で試せる」実践的な内容にする
- 絵文字は1-2個だけ使う（多すぎない）
- 景表法に抵触する誇大表現は絶対に使わない
- 最後に「今日の一歩」として簡単なアクションを提案する"""

PLATFORM_PROMPTS = {
    "twitter": """上記のテーマについて、Twitter(X)用の投稿を作成してください。
- 140文字以内（日本語）
- ハッシュタグ3つ付ける（#AI活用 #50代 + テーマに合うもの1つ）
- 読んだ人が「へえ！」と思う一言で始める
- 投稿テキストのみを出力（説明不要）""",

    "threads": """上記のテーマについて、Threads用の投稿を作成してください。
- 300文字程度
- Twitterより少し詳しく、具体例を1つ入れる
- 読みやすい改行を入れる
- 最後に「試してみて！」的な一言を添える
- 投稿テキストのみを出力（説明不要）""",

    "line": """上記のテーマについて、LINE配信用のメッセージを作成してください。
- 500文字程度
- 挨拶（おはようございます）から始める
- コピペで使える具体的なAIプロンプトテンプレートを1つ含める
- テンプレートは「」で囲んで目立たせる
- 「今日の一歩」として5分で試せるアクションを提案
- 温かく親しみやすいトーンで
- 配信テキストのみを出力（説明不要）""",
}


def _get_today_topic() -> str:
    """Get today's topic based on day-of-year rotation."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    idx = day_of_year % len(TOPIC_CATEGORIES)
    return TOPIC_CATEGORIES[idx]


async def generate_daily_tips() -> dict[str, str]:
    """Generate daily AI tips for all platforms.

    Returns:
        Dict with keys: 'twitter', 'threads', 'line', 'topic'
    """
    topic = _get_today_topic()
    logger.info(f"[DAILY_TIPS] Generating content for topic: {topic}")

    if not settings.anthropic_api_key:
        logger.warning("[DAILY_TIPS] Anthropic API key not set, using fallback")
        return _fallback_content(topic)

    results = {"topic": topic}

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        for platform, platform_prompt in PLATFORM_PROMPTS.items():
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": f"今日のテーマ: 「{topic}」\n\n{platform_prompt}",
                }],
                temperature=0.8,
            )
            results[platform] = response.content[0].text.strip()
            logger.info(f"[DAILY_TIPS] Generated {platform} content ({len(results[platform])} chars)")

    except Exception as e:
        logger.error(f"[DAILY_TIPS] Content generation failed: {e}")
        return _fallback_content(topic)

    return results


def _fallback_content(topic: str) -> dict[str, str]:
    """Fallback content when Claude API is unavailable."""
    return {
        "topic": topic,
        "twitter": f"今日のAI活用ヒント: {topic}。難しそう？実はコピペだけでできます。まずは1回試してみてください。 #AI活用 #50代 #業務効率化",
        "threads": f"おはようございます。\n\n今日のAI活用テーマは「{topic}」です。\n\n「AIは難しい」と思っていませんか？\n実は日本語で"お願い"するだけで、驚くほど簡単に使えます。\n\n今日の一歩: ChatGPT（無料版でOK）を開いて、「{topic}について教えて」と聞いてみてください。",
        "line": f"おはようございます！\n\n今日のAI活用テーマは\n「{topic}」です。\n\nAIは難しそうに見えますが、実はコピペするだけで誰でも使えます。\n\n今日のコピペテンプレート:\n「{topic}について、初心者にもわかるように3つのステップで教えてください」\n\nこれをChatGPTに貼り付けるだけです。\n\n今日の一歩:\n上のテンプレートをコピーして、ChatGPT（無料版でOK）に貼り付けてみてください。5分で新しい発見がありますよ。",
    }
