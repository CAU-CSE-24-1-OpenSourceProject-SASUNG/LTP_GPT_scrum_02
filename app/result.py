from app.Init import session
from app.service.FeedbackService import FeedbackService
from app.service.GameService import GameService
from app.service.QueryService import QueryService
from app.service.RiddleService import RiddleService
from app.service.TotalFeedbackService import TotalFeedbackService
from app.service.UserService import UserService

userService = UserService(session)
gameService = GameService(session)
riddleService = RiddleService(session)
queryService = QueryService(session)
feedbackService = FeedbackService(session)
totalFeedbackService = TotalFeedbackService(session)

users = userService.get_all_user()
for user in users:
    print("User ID :", user.user_id)
    user_games = gameService.get_game_by_user(user.user_id)
    for user_game in user_games:
        game = gameService.get_game(user_game.game_id)
        print("Game ID :", game.game_id, ", Riddle ID :", game.riddle_id)
        game_queries = queryService.get_query_by_game(game.game_id)
        for game_query in game_queries:
            query = queryService.get_query(game_query.query_id)
            print("Query :", query.query, ", Response :", query.response)
        # print("\n")
    print("\n")
