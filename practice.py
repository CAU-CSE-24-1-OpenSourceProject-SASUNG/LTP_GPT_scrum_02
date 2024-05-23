from app import ltp_gpt
from app.Init import session
from app.service.RiddlePromptingService import RiddlePromptingService
from app.service.RiddleService import RiddleService

riddleService = RiddleService(session)
rpService = RiddlePromptingService(session)


def get_embeddings(problem, situation, answer):
    problem_embedding = ltp_gpt.generate_embedding(problem)
    situation_embedding = [ltp_gpt.generate_embedding(sentence.strip()) for sentence in situation]
    answer_embedding = ltp_gpt.generate_embedding(answer)

    return problem_embedding, situation_embedding, answer_embedding


problem = "어떤 아이가 아파트 10층에 살고 있으며, 맑은 날에는 엘리베이터에서 6층에서 내려서 10층까지 걸어 올라간다. 그러나 날씨가 좋지 않다면 10층에서 내려서 집으로 간다. 어떤 상황일까?"
situation = [
    "아이는 키가 매우 작다.",
    "날씨가 좋지 않다면 아이는 우산을 들고 있다.",
    "아이는 팔이 짧다.",
    "아이는 운동하는 것을 싫어한다.",
    "만약 아이가 6층에서 내렸다면 엘리베이터를 혼자 탄 것이다.",
    "아이는 10층에 산다.",
    "아이의 나이는 6살 정도이다.",
    "엘리베이터 버튼은 높이 있다.",
    "아이는 우산으로 엘리베이터 10층 버튼을 누른다.",
    "아이는 엘리베이터 6층 버튼까지만 손이 닿습니다."
  ]
answer = "아이는 키가 작아 10층 버튼까지 손이 닿지 않습니다. 따라서 최대 6층까지만 버튼을 누를 수 있습니다. 맑지 않은 날에는 우산이 있어 아이는 우산으로 10층 버튼을 누를 수 있습니다"
progress_sentences = ["1", "2", "3"]

problem_embedding, situation_embedding, answer_embedding = get_embeddings(problem, situation, answer)
riddle_id = riddleService.create_riddle("tlsgusdn4818@gmail.com", "riddleTitle", problem, situation, answer,
                                        progress_sentences, problem_embedding, situation_embedding,
                                        answer_embedding)

print(problem_embedding)
print(situation_embedding)
print(answer_embedding)