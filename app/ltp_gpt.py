import openai
import os
import json
from dotenv import load_dotenv
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# JSON 파일 경로
umbrella_data = load_data('./app/puzzles/umbrella.json')  # Umbrella 임베딩 / 프롬프팅
listenling_data = load_data('./app/puzzles/listening.json') #  listening 임베딩 / 프롬프팅
gpt_data = load_data('./app/puzzles/GPT_answer.json') # GPT 대답 말투 프롬프팅

# 임베딩 string 가져오기
problem = umbrella_data['problem']
situation = umbrella_data['situation']
answer = umbrella_data['answer']
messages = umbrella_data['messages']
gpt_ans = gpt_data['gpt_ans'] # 말투 프롬프팅

model = 'gpt-3.5-turbo'

def generate_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return openai.embeddings.create(input=text, model=model).data[0].embedding

def similarity(embedding1, embedding2):
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    magnitude1 = sum(a ** 2 for a in embedding1) ** 0.5
    magnitude2 = sum(b ** 2 for b in embedding2) ** 0.5
    return dot_product / (magnitude1 * magnitude2)


problem_embedding = generate_embedding(problem)
situation_sentences = situation.split(".")
situation_embeddings = [generate_embedding(sentence.strip()) for sentence in situation_sentences]
answer_embedding = generate_embedding(answer)

# Embedding, 1차 프롬프팅
def evaluate_question(question):
    question_embedding = generate_embedding(question)

    problem_similarity = similarity(question_embedding, problem_embedding)
    situation_similarities = [similarity(question_embedding, emb) for emb in situation_embeddings]
    max_similarity = max(situation_similarities)
    answer_similarity = similarity(question_embedding, answer_embedding)
    
    print('정답 유사도 = ' + str(answer_similarity))
    print('문제 유사도 = ' + str(problem_similarity))
    print(situation_similarities)
    print('상황 유사도 = ' + str(max_similarity))

    if problem_similarity >= 0.8:    # 긍정
        return '맞습니다.'
    elif problem_similarity >= 0.6:
        return '그렇다고 볼 수도 있습니다.'
    else:
        count = 0
        for i in range(len(situation_sentences)):
            situation_similarity = similarity(question_embedding, situation_embeddings[i])
            if situation_similarity >= 0.4:
                count += 1
        print("count : " + str(count))
        if count == 0:
            return '문제의 정답과 상관이 없습니다.'
        else:
            message = messages + gpt_ans + [{"role": "user", "content": question}]
            response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=message,
                    temperature=0.0,
                    top_p=0.5
                    )
            return response.choices[0].message.content

# 2차 프롬프팅
gpt_similarity = load_data('./app/puzzles/gpt_similarity.json') # GPT 유사도 검증
similarity_messages = gpt_similarity['gpt_similarity']
def evaluate_similarity(question, prompting):

    sentences = prompting.split('$')
    num_sentence = len(sentences)
    prompt_sentence = f"{num_sentence}개의 문장이 있습니다. "

    for i in range(num_sentence):
        prompt_sentence += f"{i + 1}번째 문장입니다: ({sentences[i]}) "
    
        similarity_message = [{"role": "system", "content": prompt_sentence}] + similarity_messages + [{"role": "user", "content": question}]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=similarity_message,
            temperature=0.0,
            top_p=0.5
        )
    ans = response.choices[0].message.content
    
    ####
    print("####여기는 GPT 응답####")
    print(ans)
    print()
    
    #return ans
    myList = []
    myDictionary = {}
    index_sharp = ans.find('#')
    ans = ans[index_sharp:]
    
    ####
    print("####여기는 마지막 출력부분####")
    print(ans)
    print()
    
    TrueMatches = re.finditer("True", ans)
    FalseMatches = re.finditer("False", ans)
    
    for match in TrueMatches:
        myDictionary[match.start()] = True
    for match in FalseMatches:
        myDictionary[match.start()] = False
    myDictionary = dict(sorted(myDictionary.items()))
    
    ####
    print("####여기는 T/F가 나타난 index와 결과가 저장된 딕셔너리####")
    print(myDictionary)
    print()

    values = list(myDictionary.values())
    for i in range (len(values)):
        myList.append(values[i])

    ####
    print("####여기는 T/F 결과####")
    print(myList)
    print() 

    percent = 100
    for i in range(len(myList), -1, -1):
        if(myList[i] == True):
            return str(percent) + "%"
        percent -= int((100 / lem(myList)))
    return str(percent) + "%"
