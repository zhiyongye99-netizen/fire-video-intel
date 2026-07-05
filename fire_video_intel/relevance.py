from typing import Iterable


HIGH_VALUE_TERMS = {
    "firefighter",
    "firefighters",
    "fireground",
    "incident command",
    "flashover",
    "backdraft",
    "ventilation",
    "flow path",
    "structure fire",
    "high-rise fire",
    "wildland fire",
    "hazmat",
    "search and rescue",
    "scba",
    "mayday",
    "rit",
    "ric",
    "ul fsri",
    "nfpa",
    "nist",
    "niosh",
    "消防",
    "灭火救援",
    "火灾",
    "指挥",
    "内攻",
    "轰燃",
    "回燃",
    "排烟",
    "搜救",
    "危化品",
    "高层建筑火灾",
}


def score_fire_relevance(title: str, description: str, tags: Iterable[str]) -> int:
    haystack = " ".join([title, description, " ".join(tags)]).lower()
    score = 0
    for term in HIGH_VALUE_TERMS:
        if term.lower() in haystack:
            score += 2 if " " in term or term in {"消防", "灭火救援", "轰燃", "回燃"} else 1
    return min(score, 10)


def is_fire_related(title: str, description: str, tags: Iterable[str], threshold: int = 2) -> bool:
    return score_fire_relevance(title, description, tags) >= threshold

