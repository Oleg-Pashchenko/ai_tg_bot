import openai
import secure_data


def get_answer(messages):
    try:
        openai.api_key = secure_data.OPENAI_API_KEY
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=messages,

        )
        if response['choices'][0]['message']['content'].count('?') > 1:
            return get_answer(messages)
        return response['choices'][0]['message']['content']

    except Exception as e:
        print('Ошибка', e)
        return get_answer(messages)