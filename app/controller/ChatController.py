from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.auth.authenticate import authenticate
from app.auth.jwt import *
from app.domain.dto.QueryInfoDto import QueryInfoDto
from app.service.GameQueryService import GameQueryService
from app.service.GameService import GameService
from app.service.QueryService import QueryService
from app.service.RankingService import RankingService
from app.service.UserService import UserService
from app.util.util import *


def get_chat_router(userService: UserService, gameService: GameService, queryService: QueryService,
                    gqService: GameQueryService, rankingService: RankingService):
    router = APIRouter()

    # 채팅(질문)
    @router.post("/")
    async def chat(request: Request, queryInfo: QueryInfoDto):
        try:
            token = get_token_from_header(request)
            user_email = await authenticate(token)
            user_id = userService.get_user_email(user_email)
            query = queryInfo.query
            game_id = queryInfo.game_id
            game = gameService.get_game(game_id)
            riddle = game.riddle
            if game.query_ticket > 0:  # query 개수 제한
                # TODO 메모이제이션
                response = ltp_gpt.evaluate_question(query, riddle)  # 1차 프롬프팅
                query_id = queryService.create_query(query, response)  # query 생성
                gqService.create_game_query(game_id, query_id)  # game_query 생성 : query ticket -= 1
                # print(response)
                if '맞습니다' in response or '정답과 유사합니다' in response:
                    similarity = ltp_gpt.evaluate_similarity(query, riddle)  # 2차 프롬프팅
                    gameService.set_progress(game_id, similarity)  # game 진행도 업데이트
                    if game.is_first is True and game.progress == 100:  # 정답일 때
                        correct_time = datetime.datetime.now() - datetime.datetime.strptime(
                            request.session.get('game_start_time'), "%Y-%m-%d %H:%M:%S")
                        gameService.correct_game(game_id, correct_time)
                        game = gameService.get_game(game_id)
                        rankingService.update_ranking(game)  # 랭킹 업데이트
                        userService.level_up(user_id)  # 경험치 증가
                return JSONResponse(content={"queryId": query_id, "response": response})
                # return JSONResponse(content={"queryId": query_id, "queryCount": game.query_ticket, "response": response})
            else:
                return JSONResponse(content={'error': "Failed to create query"}, status_code=400)
        except Exception as e:
            print(str(e))
            return JSONResponse(content={"error": str(e)}, status_code=500)

    return router
