"""REST API for the future website."""

from aiohttp import web
from services.database import get_db
from services.team_matcher import get_all_team_names, get_team_info


async def handle_get_matches(request):
    """GET /api/matches - list all matches."""
    db = get_db()
    matches = await db.get_all_matches()
    return web.json_response({"matches": matches, "count": len(matches)})


async def handle_get_match(request):
    """GET /api/matches/{match_id} - match details."""
    match_id = request.match_info['match_id']
    db = get_db()
    match = await db.get_match_by_id(match_id)
    if match:
        return web.json_response(match)
    return web.json_response({"error": "Матч не найден"}, status=404)


async def handle_get_teams(request):
    """GET /api/teams - list all teams."""
    teams = get_all_team_names()
    return web.json_response({"teams": teams, "count": len(teams)})


async def handle_get_team_info(request):
    """GET /api/teams/{team} - team info."""
    team = request.match_info['team']
    info = get_team_info(team)
    if info:
        return web.json_response({"team": team, "info": info})
    return web.json_response({"error": "Команда не найдена"}, status=404)


async def handle_subscribe(request):
    """POST /api/subscribe - subscribe via site."""
    data = await request.json()
    chat_id = data.get("chat_id")
    sub_type = data.get("type")
    value = data.get("value")

    if not chat_id or not sub_type or not value:
        return web.json_response({"error": "Неверные параметры"}, status=400)

    db = get_db()
    success = await db.subscribe(chat_id, sub_type, value)

    if success:
        return web.json_response({"status": "ok", "message": "Подписка оформлена"})
    return web.json_response({"status": "already_subscribed"})


def create_api_app():
    """Create API application."""
    app = web.Application()
    app.router.add_get('/api/matches', handle_get_matches)
    app.router.add_get('/api/matches/{match_id}', handle_get_match)
    app.router.add_get('/api/teams', handle_get_teams)
    app.router.add_get('/api/teams/{team}', handle_get_team_info)
    app.router.add_post('/api/subscribe', handle_subscribe)
    return app


if __name__ == "__main__":
    app = create_api_app()
    web.run_app(app, host="0.0.0.0", port=8080)