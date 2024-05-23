import json
import os
import re

import openai
from dotenv import load_dotenv

from app.Init import session
from .service.RiddlePromptingService import RiddlePromptingService
from .service.UserService import UserService

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
model = 'gpt-3.5-turbo'


def generate_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return openai.embeddings.create(input=text, model=model).data[0].embedding


def similarity(embedding1, embedding2):
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    magnitude1 = sum(a ** 2 for a in embedding1) ** 0.5
    magnitude2 = sum(b ** 2 for b in embedding2) ** 0.5
    return dot_product / (magnitude1 * magnitude2)


userService = UserService(session)
riddlePromptingService = RiddlePromptingService(session)


# Embedding, 1차 프롬프팅
def evaluate_question(question, riddle):
    problem_embedding = json.loads(riddle.problem_embedding_str)
    situation_embedding = json.loads(riddle.situation_embedding_str)
    answer_embedding = json.loads(riddle.answer_embedding_str)
    question_embedding = generate_embedding(question)

    problem_similarity = similarity(question_embedding, problem_embedding)
    situation_similarities = [similarity(question_embedding, emb) for emb in situation_embedding]
    max_similarity = max(situation_similarities)
    answer_similarity = similarity(question_embedding, answer_embedding)

    print('정답 유사도 = ' + str(answer_similarity))
    print('문제 유사도 = ' + str(problem_similarity))
    # print(situation_similarities)
    print('상황 유사도 = ' + str(max_similarity))

    if problem_similarity >= 0.8:  # 긍정
        return '맞습니다.'
    elif problem_similarity >= 0.6:
        return '그렇다고 볼 수도 있습니다.'
    else:
        count = 0
        for i in range(len(situation_embedding)):
            situation_similarity = similarity(question_embedding, situation_embedding[i])
            if situation_similarity >= 0.4:
                count += 1
        print("count : " + str(count))
        if count == 0:
            return '문제의 정답과 상관이 없습니다.'
        else:
            # gpt_prompting = "당신은 상황 유추 퀴즈 게임의 진행자 입니다. 플레이어는 퀴즈의 정답을 맞추기 위해 당신에게 질문할 것입니다. 당신은 플레이어의 질문이 아래의 문제와 상황에 논리적으로 일치하거나 유사한지 판단해야 합니다."
            gpt_prompting = "당신은 질문자가 물어보는 질문에 대해 서술형으로 대답해야 합니다. 다음 규칙에 따라 [결론]을 판단해 주세요. 당신이 해야 할 출력 형식은 다음과 같습니다. ([1] 사용자 입력: <사용자 입력 내용>, [2] 사용자 입력과 문장들과의 비교: <비교 내용>, [3]: 결론: <결론 내용>) <사용자 입력 내용>은 사용자가 당신에게 질문한 내용입니다. <비교 내용>은 사용자의 질문과 문제/상황/정답 간의 유사성을 step by step으로 설명합니다. <결론 내용>은 <비교 내용>에 의거하여 (맞습니다.), (그렇다고 볼 수도 있습니다.), (아닙니다.), (모르겠습니다.), (문제의 정답과 상관이 없습니다.) 중 하나로 출력해주세요."
            problem_sentence = "문제:(" + riddle.problem + ")"
            # print(problem_sentence)
            situation_sentence = "상황:(" + riddle.situation + ")"
            # print(situation_sentence)
            ans_sentence = "답안:(" + riddle.answer + ")"
            # print(ans_sentence)
            gpt_prompting += problem_sentence
            gpt_prompting += situation_sentence
            gpt_prompting += ans_sentence
            assistants = riddlePromptingService.get_all_prompting(riddle.riddle_id)
            assistant_prompting = []
            for i in assistants:
                assistant_prompting.append({"role": "user", "content": i.user_query})
                # print(i.user_query)
                assistant_prompting.append({"role": "assistant", "content": i.assistant_response})
                # print(i.assistant_response)
            message = [{"role": "system", "content": gpt_prompting}] + assistant_prompting + [
                {"role": "user", "content": question}]
            # print(message)
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message,
                temperature=0.0,
                top_p=0.5
            )
            GPT_response = response.choices[0].message.content
            print('질문 : ' + question)
            print('응답 : ' + GPT_response)
            if '맞습니다' in GPT_response:
                return '맞습니다.'
            elif '그렇다고 볼 수도 있습니다' in GPT_response:
                return '그렇다고 볼 수도 있습니다.'
            elif '아닙니다' in GPT_response:
                return '아닙니다.'
            elif '모르겠습니다' in GPT_response:
                return '모르겠습니다.'
            elif '정확한 정답을 맞추셨습니다' in GPT_response:
                return '정확한 정답을 맞추셨습니다.'
            elif '문제의 정답과 상관이 없습니다' in GPT_response:
                return '문제의 정답과 상관이 없습니다.'
            elif '정답과 유사합니다' in GPT_response:
                return '정답과 유사합니다.'
            return '문제의 정답과 상관이 없습니다.'


def evaluate_similarity(question, riddle):
    sentences = riddle.progress_sentences.split('$')
    for sentence in sentences:
        print(sentence)
    num_sentence = len(sentences)
    prompt_sentence = f"{num_sentence}개의 문장이 있습니다. "
    for i in range(num_sentence):
        prompt_sentence += f"{i + 1}번째 문장입니다: ({sentences[i]}) "

    # prompt_sentence += "당신은 문장 맞추기 퀴즈 시스템의 진행자입니다. 이 시스템의 참여자인 플레이어는 퀴즈의 정답을 맞추기 위해 질문을 할 것입니다. 플레이어에게 문장을 입력 받으면 입력받은 문장을 우선 출력해주세요. 당신은 플레이어의 질문이 앞서 말한 5개의 문장과 논리적으로 일치한지 판단해야 합니다. 플레이어의 질문과 완전히 똑같은 의미의 문장은 True, 플레이어의 질문과 의미적으로 조금 다르거나, 아예 관련이 없는 문장은 False로 대답해야 하고, 그를 위해서 다음과 같은 과정을 밟아주세요: 1. 모든 문장 하나하나씩 플레이어의 질문과의 유사성을 step by step으로 매우 자세하게 설명하세요. 2. 모든 문장에 대해 True/False를 판단하세요. 모든 문장에 대해 평가를 수행해야 합니다. 3. 최종 결과를 형식에 맞춰 제공하세요. 최종 결과 형식은 반드시 아래와 같습니다: '#(1번 문장과 플레이어의 질문): <True/False>, #(2번 문장과 플레이어의 질문): <True/False>, #(3번 문장과 플레이어의 질문): <True/False>, #(4번 문장과 플레이어의 질문): <True/False>, #(5번 문장과 플레이어의 질문): <True/False>'. 모든 문장에 대해 True/False 평가를 반드시 포함해야 합니다."
    prompt_sentence += "당신은 문장 맞추기 퀴즈 시스템의 진행자입니다. 이 시스템의 참여자인 플레이어는 퀴즈의 정답을 맞추기 위해 질문을 할 것입니다. 플레이어에게 질문을 받으면 다음 규칙에 따라 [결론]을 판단해 주세요. 당신이 해야 할 출력 형식은 다음과 같습니다. ([1] 사용자 입력: <사용자 입력 내용>, [2] 1번 문장과 사용자 입력의 비교: <1번 문장과의 비교 내용>, 2번 문장과 사용자 입력의 비교: <2번 문장과의 비교 내용>, ..., n번 문장과 사용자 입력의 비교: <n번 문장과의 비교 내용> [3] 결론: #1번 문장과의 결론: <1번 문장과의 결론 내용>, #2번 문장과의 결론: <2번 문장과의 결론 내용>, ..., #n번 문장과의 결론: <n번 문장과의 결론 내용>) <사용자 입력 내용>은 사용자가 당신에게 질문한 내용입니다. <비교 내용>은 사용자의 질문이 앞서 언급한 문장 모두 각각 정확히 같은 의미를 갖는지 step by step으로 설명합니다. <결론 내용>은 각 문장에 따라 True, False 중 하나로 대답합니다. n은 비교해야 할 문장의 개수입니다. 즉 당신은 n개의 문장이 있으면 [2]와 [3]에서 반드시 n개의 출력을 해야 합니다. 플레이어에게 문장을 입력 받으면 입력받은 문장을 우선 출력해주세요. 당신은 플레이어의 질문이 앞서 말한 문장들과 논리적으로 일치한지 판단해야 합니다. 플레이어의 질문과 완전히 똑같은 의미의 문장은 True, 플레이어의 질문과 의미적으로 조금 다르거나, 아예 관련이 없는 문장은 False로 대답해야 합니다. 이전에 알려준 모든 문장 하나하나씩 플레이어의 질문과의 유사성을 step by step으로 매우 자세하게 설명하세요. 문장이 동일한 의미이면 동일한 이유를, 다른 의미이면 다른 이유를 각각의 문장 하나하나 마다 설명해 주시길 바랍니다. 즉 n개의 문장이 있으면 n번의 유사성 검증으로 출력해 주세요. 그리고 각 비교 마다 True/False 여부를 출력해 주세요. 형식은 다음과 같습니다:  #(1번 문장과의 비교): (1번문장과의 비교 논리, <True/False>), #(2번 문장과의 비교): (2번 문장과의 비교 논리, <True/False>), ..."
    similarity_message = [{"role": "system", "content": prompt_sentence}, {"role": "user", "content": question}]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=similarity_message,
        temperature=0.0,
        top_p=0.5
    )
    ans = response.choices[0].message.content

    # TODO : index error로 인해 유사도 값이 return X
    ####
    # print("####여기는 GPT 응답####")
    # print("GPT 응답 : " + ans)
    # print()

    # return ans
    myList = []
    myDictionary = {}
    index_sharp = ans.find('#')
    ans = ans[index_sharp:]

    ####
    # print("####여기는 마지막 출력부분####")
    # print(ans)
    # print()

    TrueMatches = re.finditer("True", ans)
    FalseMatches = re.finditer("False", ans)

    for match in TrueMatches:
        myDictionary[match.start()] = True
    for match in FalseMatches:
        myDictionary[match.start()] = False
    myDictionary = dict(sorted(myDictionary.items()))

    ####
    # print("####여기는 T/F가 나타난 index와 결과가 저장된 딕셔너리####")
    # print(myDictionary)
    # print()

    values = list(myDictionary.values())
    for i in range(len(values)):
        myList.append(values[i])

    ####
    # print("####여기는 T/F 결과####")
    # print(myList)
    # print()

    percent = 100
    for i in range(len(myList), -1, -1):
        if myList[i] is True:
            return percent
        percent -= int((100 / len(myList)))
    return percent
