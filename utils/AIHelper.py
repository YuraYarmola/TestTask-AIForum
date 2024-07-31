from detoxify import Detoxify
from AIForum import settings
from openai import OpenAI


def is_text_toxic(text: str) -> bool:
    results = Detoxify('multilingual').predict(text)
    if results.get('toxicity') > 0.8:
        return True
    else:
        return False


def comment_reply(post: str, comment: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        messages=[
            {"role": "user", "content": f"""Your job is to make short reply for comment for post
    POST: {post}
    
    COMMENT: {comment}"""}
        ]
    )

    return completion.choices[0].message.content

