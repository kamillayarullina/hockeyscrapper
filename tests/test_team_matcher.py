from services.team_matcher import (
    extract_teams_from_title,
    get_team_info,
    get_all_team_names,
    normalize_team_name,
)


class TestExtractTeamsFromTitle:

    def test_extract_two_teams(self):
        result = extract_teams_from_title("СКА – ЦСКА")
        assert sorted(result) == ["СКА", "ЦСКА"]

    def test_extract_single_team(self):
        result = extract_teams_from_title("Матч Ак Барс – Салават Юлаев")
        assert sorted(result) == ["Ак Барс", "Салават Юлаев"]

    def test_empty_title(self):
        assert extract_teams_from_title("") == []

    def test_none_title(self):
        assert extract_teams_from_title(None) == []

    def test_no_team_match(self):
        result = extract_teams_from_title("Random non-hockey event")
        assert result == []

    def test_partial_word_no_match(self):
        result = extract_teams_from_title("Армейцы-краснаямашина")
        assert "ЦСКА" in result

    def test_team_in_compound_word_should_not_match(self):
        result = extract_teams_from_title("Тракторист против Динамович")
        assert "Трактор" not in result

    def test_lowercase_input(self):
        result = extract_teams_from_title("ска – цска")
        assert sorted(result) == ["СКА", "ЦСКА"]

    def test_team_names_with_punctuation(self):
        result = extract_teams_from_title("СКА — ЦСКА!")
        assert sorted(result) == ["СКА", "ЦСКА"]

    def test_city_variant(self):
        result = extract_teams_from_title("Казань – Омск")
        assert sorted(result) == ["Авангард", "Ак Барс"]

    def test_all_teams_have_team_name(self):
        for team in get_all_team_names():
            assert extract_teams_from_title(team) == [team]


class TestGetTeamInfo:

    def test_valid_team(self):
        info = get_team_info("СКА")
        assert info is not None
        assert info["venue"] == "СКА Арена"
        assert info["city"] == "Санкт-Петербург"

    def test_none_team(self):
        assert get_team_info(None) is None

    def test_empty_team(self):
        assert get_team_info("") is None

    def test_unknown_team(self):
        assert get_team_info("Unknown Team") is None

    def test_all_teams_have_venue_and_city(self):
        for team in get_all_team_names():
            info = get_team_info(team)
            assert info is not None
            assert "venue" in info
            assert "city" in info


class TestGetAllTeamNames:

    def test_returns_list(self):
        teams = get_all_team_names()
        assert isinstance(teams, list)
        assert len(teams) > 0

    def test_includes_known_teams(self):
        teams = get_all_team_names()
        assert "СКА" in teams
        assert "ЦСКА" in teams
        assert "Ак Барс" in teams


class TestNormalizeTeamName:

    def test_normalize_canonical_name(self):
        assert normalize_team_name("СКА") == "СКА"

    def test_normalize_variant(self):
        assert normalize_team_name("питер") == "СКА"

    def test_normalize_lowercase(self):
        assert normalize_team_name("спартак") == "Спартак"

    def test_normalize_with_whitespace(self):
        assert normalize_team_name("  цска  ") == "ЦСКА"

    def test_none_input(self):
        assert normalize_team_name(None) is None

    def test_empty_input(self):
        assert normalize_team_name("") is None
