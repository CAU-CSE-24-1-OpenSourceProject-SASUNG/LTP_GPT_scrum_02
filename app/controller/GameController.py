import datetime

from fastapi import Query, APIRouter
from starlette.responses import JSONResponse

from app.auth.authenticate import authenticate
from app.service.GameQueryService import GameQueryService
from app.service.GameService import GameService
from app.service.RiddleService import RiddleService
from app.service.UserGameService import UserGameService
from app.service.UserService import UserService
from app.util.util import *


def get_game_router(userService: UserService, gameService: GameService, ugService: UserGameService,
                    gqService: GameQueryService, riddleService: RiddleService):
    router = APIRouter()

    # 사이드바에 최근 게임 목록
    @router.get('/list')
    async def lookup(request: Request):
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)
        games = ugService.get_recent_games(user.user_id)
        recent_games = [{'gameId': game.game_id, 'gameTitle': game.title} for game in games]
        return JSONResponse(content=recent_games)

    # 가장 최근 게임 접속
    @router.get('/recent')
    async def access(request: Request):
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)
        game = ugService.get_recent_game(user.user_id)
        # gameService.reaccess(game.game_id)
        return JSONResponse(content={'gameId': game.game_id})

    # 새로운 게임 생성
    @router.post('/new')
    async def create_game(request: Request):
        try:
            body = await request.json()
            riddle_id = body.get("riddleId")
            token = get_token_from_header(request)
            user_email = await authenticate(token)
            user = userService.get_user_email(user_email)
            request.session['game_start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if userService.create_game(user.user_id) is True:
                game_id = gameService.create_game(user.user_id, riddle_id)  # game 생성
                ugService.create_user_game(user.user_id, game_id)  # user_game 생성
                return JSONResponse(content={'newGameId': game_id})
            else:
                return JSONResponse(content={'error': "Failed to create game"}, status_code=400)
        except Exception as e:
            print(str(e))
            return JSONResponse(content={"error": str(e)}, status_code=404)

    # 게임 진행률 조회
    @router.get('/progress')
    async def progress(request: Request):
        try:
            body = await request.json()
            game_id = body.get('gameId')
            game = gameService.get_game(game_id)
            return JSONResponse(content={'progress': game.progress})
        except Exception as e:
            print(str(e))
            return JSONResponse(content={"error": str(e)}, status_code=404)

    # 게임 접속하기
    @router.get('/info')
    async def access_game(request: Request, gameId: str = Query(...)):
        try:
            token = get_token_from_header(request)
            user_email = await authenticate(token)
            user = userService.get_user_email(user_email)
            game = gameService.get_game(gameId)
            riddle = riddleService.get_riddle(game.riddle_id)
            game_queries = gqService.get_queries(gameId)
            queries = [game_query.query for game_query in game_queries]
            queries.sort(key=lambda x: x.createdAt)  # query 생성 시각 순으로 오름차순 정렬
            game_info = [{'gameTitle': game.title, 'problem': riddle.problem}]
            for query in queries:
                game_info.append({
                    'queryId': query.query_id,
                    'query': query.query,
                    'response': query.response
                })
            return JSONResponse(content=game_info)
        except Exception as e:
            print(str(e))
            return JSONResponse(content={"error": str(e)}, status_code=404)

    return router
