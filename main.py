"""FastAPI service for testing japanese flashcards."""

import argparse
import logging
import os
import sys
import multiprocessing
import time
import uvicorn
import urllib.request
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from urllib.error import URLError

import fastapi
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gaku.api_types import (
    NextCardMessage,
    TestStatusMessage,
    GeneratedImports,
    ImportRequest,
    StartTestRequest,
    CardFilter,
)
from gaku.gaku_manager import GakuManager
from gaku.card_types import (
    CardSource,
    TestCardTypes,
    BaseCard,
    create_card_from_json,
)
from gaku.question import TestAnswer

logging.basicConfig(level=logging.INFO)


# get the working directory
if getattr(sys, "frozen", False):
    # running in pyinstaller bundle
    app_dir = Path(sys._MEIPASS)  # type: ignore
    logging.info(str(app_dir.resolve()))
    # since the pyinstaller will have main dir in _
    userdata_dir = app_dir.parent / "userdata"
else:
    # normal Python environment
    app_dir = Path(__file__).parent
    userdata_dir = app_dir / "userdata"


# set gaku data locations
resource_dir = app_dir / "resources"
frontend_path = resource_dir / "www"


manager = GakuManager(workdir=app_dir, userdata=userdata_dir)


@asynccontextmanager
async def startup_teardown(app: FastAPI) -> AsyncGenerator:
    """Startup and teardown actions.

    Parameters
    ----------
    app: FastAPI
        The FastAPI app.
    """
    manager.load_test_session()
    yield
    manager.save_test_session()


app = FastAPI(lifespan=startup_teardown)
api_router = APIRouter(prefix="/api")

if os.getenv("API_DEV", "0") == "1":
    # allow anything - dev use only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class CardSourceLinkRequest(BaseModel):
    """Mapping for attaching source to card."""

    card_id: str
    source_id: str


# High level structure
# - card editor
# - test session


# card editor
# - get all cards
# - add card
# - edit card
# - delete card
# - save cards to file
@api_router.get("/cards")
async def get_cards() -> list[TestCardTypes]:
    """Get all cards.
    Most recent cards are returned first.
    """
    send_cards = manager.db.get_cards_any_state()
    send_cards.reverse()
    logging.info(f"Sending {len(send_cards)} cards")
    return send_cards


@api_router.post("/cards/add")
async def add_card(card: dict) -> dict:
    """Add card.

    Parameters
    ----------
    card: dict
        The card to add

    Returns
    -------
    dict
        Dictionary with status and card_id fields.
    """
    if "card_id" in card and card["card_id"] != "":
        raise HTTPException(
            status_code=400, detail="ID should not be provided for new card"
        )
    logging.info(f"Creating card from: {card}")
    test_card = create_card_from_json(card)
    manager.db.add_card(test_card)
    logging.info(f"Added card: {test_card}")
    return {"status": "ok", "card_id": test_card.card_id}


@api_router.post("/cards/update")
async def edit_card(card: dict) -> dict:
    """Edit card.

    Parameters
    ----------
    card: dict
        Dictionary with the card to update.

    Returns
    -------
    dict
        Dictionary with status field.
    """
    updated_card = create_card_from_json(card)
    manager.db.update_card(updated_card)
    logging.info(f"Updated card: {updated_card}")
    return {"status": "ok"}


@api_router.post("/cards/delete")
async def delete_card(card: BaseCard) -> dict:
    """Delete card."""
    manager.db.delete_card(card.card_id)
    logging.info(f"Deleted card: {card}")
    return {"status": "ok"}


@api_router.post("/cards/get_by_text")
async def get_cards_by_text(
    filter: CardFilter,
) -> list[TestCardTypes]:
    """Get cards by text."""
    logging.info(f"Getting cards with filter: {filter}")
    cards = manager.db.get_cards_by_text(filter=filter)
    logging.info(f"Sending {len(cards)} cards")
    return cards


@api_router.post("/cards/add_source_link")
async def add_source_link(request: CardSourceLinkRequest) -> dict:
    """Add source link to a card."""
    manager.db.add_card_source_link(request.card_id, request.source_id)
    logging.info(f"Added source link: {request.card_id} - {request.source_id}")
    return {"status": "ok"}


@api_router.post("/cards/delete_all_source_links")
async def delete_all_source_links(request: CardSourceLinkRequest) -> dict:
    """Delete all source links for a card."""
    manager.db.delete_all_card_source_links(request.card_id)
    logging.info(f"Deleted all source links for card: {request.card_id}")
    return {"status": "ok"}


# @api_router.post("/cards/add_source_link")
# async def add_source_link(card_id: str, source_id: str):
#     """Add source link."""
#     manager.db.add_card_source_link(card_id, source_id)
#     return {"status": "ok"}


@api_router.post("/cards/delete_source_link")
async def delete_source_link(request: CardSourceLinkRequest) -> dict:
    """Delete source link."""
    manager.db.delete_card_source_link(request.card_id, request.source_id)
    logging.info(f"Deleted source link: {request}")
    return {"status": "ok"}


# card sources functionality
@api_router.get("/sources")
async def get_sources() -> list[dict]:
    """Get all card sources."""
    card_sources = [
        source.model_dump(mode="json") for source in manager.db.get_card_sources_list()
    ]
    logging.info(f"Sending {len(card_sources)} sources")
    return card_sources


@api_router.post("/sources/add")
async def add_source(source: dict) -> dict:
    """Add card source."""
    logging.info(f"Adding source: {source}")
    if "source_id" in source:
        if source["source_id"] != "":
            raise HTTPException(
                status_code=400, detail="ID should not be provided for new source"
            )
        source.pop("source_id")
    try:
        card_source = CardSource(**source)
        manager.db.add_card_source(card_source)
    except Exception as e:
        logging.exception(f"Failed to add source: {e}")
        raise HTTPException(status_code=400, detail="Failed to add source")
    logging.info(f"Added source: {card_source}")
    return {"status": "ok", "source_id": card_source.source_id}


@api_router.post("/sources/update")
async def update_source(source: dict) -> dict:
    """Update card source."""
    card_source = CardSource(**source)
    manager.db.update_card_source(card_source)
    logging.info(f"Updated source: {card_source}")
    return {"status": "ok"}


@api_router.post("/sources/delete")
async def delete_source(source: dict) -> dict:
    """Delete card source."""
    logging.info(f"Deleting source: {source}")
    manager.db.delete_card_source(source["source_id"])
    logging.info(f"Deleted source: {source}")
    return {"status": "ok"}


# test session
# - start test session
# - get next card
# - answer question
# - finish test session
# - get session status


@api_router.post("/test/start")
async def start_test(request: StartTestRequest) -> dict:
    """Start test session."""
    logging.info(f"Starting test session, params: {request}")

    manager.start_test_session(request)
    return {"status": "ok"}


@api_router.post("/test/start_new")
async def start_test_new(request: StartTestRequest) -> dict:
    """Start test session with new cards."""
    logging.info(f"Starting test session with new cards, params: {request}")

    manager.start_test_session_new_cards(request)
    logging.info("Started test session with new cards")
    return {"status": "ok"}


@api_router.post("/test/num_new")
async def get_num_new(request: CardFilter) -> int:
    """Get number of new cards.

    Parameters
    ----------
    card_sources : Optional[list[CardSource]]
        List of card sources to filter by.

    Returns
    -------
    int
        Number of new cards matching the sources.
    """
    new_new = manager.db.get_num_new_cards(request)
    logging.info(f"Number of new cards: {new_new}")
    return new_new


@api_router.post("/test/start_studied")
async def start_test_studied(request: StartTestRequest) -> dict:
    """Starts test session with studied cards."""
    logging.info(f"Starting test session with studied cars, params: {request}")

    manager.start_test_session(request)
    return {"status": "ok"}


@api_router.post("/test/num_studied")
async def get_num_studied(request: CardFilter) -> int:
    """Gets a number matching studied cards."""

    num_studied = manager.db.get_num_studied_cards(request)
    logging.info(f"Num studied cards: {num_studied}")
    return num_studied


@api_router.post("/test/num_any_state")
async def get_num_any_state(request: CardFilter) -> int:
    """Gets a number of cards matching filter independent of FSRS state.

    Parameters
    ----------
    request : CardFilter
        The filter to use for counting the cards
    """
    num_any_state = manager.db.get_num_cards_any_state(request)
    logging.info(
        f"Number of cards matching filter, ignoring FSRS state: {num_any_state}"
    )
    return num_any_state


@api_router.post("/test/start_due")
async def start_test_due(request: StartTestRequest) -> dict:
    """Start test session with due cards."""
    logging.info(f"Starting test session with due cards, params: {request}")

    manager.start_test_session_fsrs_due(
        test_setup=request,
    )
    logging.info("Started test session with due cards")
    return {"status": "ok"}


@api_router.post("/test/num_due")
async def get_num_due(request: CardFilter) -> int:
    """Get number of due cards."""
    num_due = manager.get_num_due_cards(request)
    logging.info(f"Number of due cards: {num_due}")
    return num_due


class RecentMistakesStartTest(BaseModel):
    """Test start configuration for recent mistakes."""

    start_request: StartTestRequest
    time_since: int


@api_router.post("/test/start_recent_mistakes")
async def start_test_recent_mistakes(request: RecentMistakesStartTest) -> dict:
    """Start test session with recent mistakes."""
    logging.info(f"Starting test session with recent mistakes, params: {request}")

    manager.start_test_session_recent_mistakes(
        test_setup=request.start_request,
        timestamp=request.time_since,
    )
    logging.info("Started test session with recent mistakes")
    return {"status": "ok"}


class RecentMistakesFilter(BaseModel):
    """Filter for recent mistakes counting."""

    filter: CardFilter
    time_since: int


@api_router.post("/test/num_recent_mistakes_since")
async def get_num_recent_mistakes_since(request: RecentMistakesFilter) -> int:
    """Get recent mistakes stats."""
    logging.info(f"Getting recent mistakes stats, params: {request}")
    recent_mistakes = manager.db.mistakes_get_num_mistakes_since(
        request.time_since, request.filter
    )
    logging.info(f"Recent mistakes stats: {recent_mistakes}")
    return recent_mistakes


@api_router.post("/test/practice_failed_cards")
async def practice_failed_cards() -> dict:
    """Practice failed cards from the last test session."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="No test session exists.")
    logging.info("Practicing failed cards")
    manager.test_session.practice_failed_cards()
    return {"status": "ok"}


@api_router.post("/test/practice_all_cards")
async def practice_all_cards() -> dict:
    """Practice all cards from the last test session."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="No test session exists.")
    logging.info("Practicing all cards")
    manager.test_session.practice_all_cards()
    return {"status": "ok"}


@api_router.get("/test/session_active")
async def get_session_active() -> dict:
    """Get test session status."""
    session_active = manager.get_session_active()
    logging.info(f"Session active: {session_active}")
    return {"session_active": session_active}


@api_router.get("/test/next")
async def get_next_card() -> NextCardMessage:
    """Get next card."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")
    next_card = manager.test_session.get_test_question()
    if next_card.next_question is None:
        # clear saved test session if current session is finished
        manager.clear_saved_test_session()
    logging.info(f"Next card: {next_card}")
    return next_card


# @api_router.get("/test/wrap_up")
# async def wrapup_test() -> dict:
#     """Wrap up test session."""
#     if not manager.get_session_active():
#         raise HTTPException(status_code=400, detail="Test session not started")
#     manager.test_session.wrap_up()
#     logging.info("Wrapped up test session")
#     return {"status": "ok"}


class AnswerMessage(BaseModel):
    """Message for answering current test question."""

    answer: TestAnswer


@api_router.post("/test/check_answer")
async def check_answer(answer_message: AnswerMessage) -> dict:
    """Check answer without answering it."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")
    answer_is_correct = manager.test_session.check_answer(answer_message.answer)
    logging.info(f"Answer is correct: {answer_is_correct}")
    return {"status": "ok", "answer_is_correct": answer_is_correct}


@api_router.post("/test/answer_question")
async def answer_question(answer_message: AnswerMessage) -> dict:
    """Answer question."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")
    answer_is_correct = manager.test_session.answer_question(answer_message.answer)
    return {"status": "ok", "answer_is_correct": answer_is_correct}


@api_router.post("/test/mark_correct")
async def mark_correct(answer: dict) -> dict:
    """Mark question as correct."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")

    if manager.test_session.current_question is None:
        raise HTTPException(status_code=400, detail="No current question")

    # verify the answer ids and current question answer ids match
    answer_ids = [
        answer.answer_id
        for group in manager.test_session.current_question.answers
        for answer in group.answers
    ]
    response_ids = list(answer.keys())
    if not set(answer_ids) == set(response_ids):
        raise HTTPException(
            status_code=400, detail="Answer ids do not match current question"
        )

    manager.test_session.mark_answer_correct(
        manager.test_session.current_question.question_id
    )
    logging.info("Marked answer as correct")
    return {"status": "ok"}


@api_router.post("/test/mark_mistake")
async def mark_mistake(answer: dict) -> dict:
    """Mark question as a mistake."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")

    if manager.test_session.current_question is None:
        raise HTTPException(status_code=400, detail="No current question")

    # verify the answer ids and current question answer ids match
    answer_ids = [
        answer.answer_id
        for group in manager.test_session.current_question.answers
        for answer in group.answers
    ]
    response_ids = list(answer["answer"].keys())
    if not set(answer_ids) == set(response_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Answer ids do not match current question, {answer_ids} != {response_ids}",
        )

    manager.test_session.mark_answer_mistake(
        manager.test_session.current_question.question_id
    )
    logging.info("Marked answer as a mistake")
    return {"status": "ok"}


@api_router.get("/test/results")
async def get_test_results() -> dict:
    """Get test results."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")
    test_results = manager.test_session.get_test_results()
    logging.info(f"Test results: {test_results}")
    return test_results


@api_router.get("/test/status")
async def get_test_status() -> TestStatusMessage:
    """Get test status."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")
    test_status = manager.test_session.get_session_status()
    logging.info(f"Test status: {test_status}")
    return test_status


@api_router.get("/test/is_practice")
async def get_is_practice() -> bool:
    """Get test status."""
    if manager.test_session is None:
        raise HTTPException(status_code=400, detail="Test session not started")
    is_practice = not manager.test_session.mark_answers
    logging.info(f"Is practice: {is_practice}")
    return is_practice


@api_router.post("/vocab/generate_vocab_import")
async def generate_vocab_import(import_data: dict) -> GeneratedImports:
    """Generate cards for vocabulary list."""
    vocab = import_data["vocab"]
    generated_imports = manager.generate_vocab_import(vocab.splitlines())
    logging.info(f"Generated {len(generated_imports.generated_cards)} cards")
    return generated_imports


@api_router.post("/vocab/import_cards")
async def import_vocab_cards(import_data: ImportRequest) -> dict:
    """Import cards."""
    logging.info(f"Importing {len(import_data.cards.generated_cards)} cards")
    manager.import_cards(import_data.cards, import_data.sources)
    return {"status": "ok"}


# stats
@api_router.get("/stats/num_due")
async def get_num_due_stats() -> dict[int, int]:
    """Get due stats."""
    due_stats = manager.get_num_upcoming_cards()
    logging.info(f"Due stats: {due_stats}")
    return due_stats


@api_router.get("/stats/num_recent_mistakes")
async def get_num_recent_mistakes() -> dict[int, int]:
    """Get recent mistakes stats."""
    recent_mistakes = manager.get_num_recent_mistakes()
    logging.info(f"Recent mistakes stats: {recent_mistakes}")
    return recent_mistakes


app.include_router(router=api_router)

# add access to frontend
if frontend_path.exists():
    frontend_router = APIRouter()

    @frontend_router.get("/{path:path}")
    async def frontend_handler(path: str) -> fastapi.responses.FileResponse:
        """Handles React frontend requests.

        Parameters
        ----------
        path: str
            Requested path

        Returns
        -------
        fastapi.responses.FileResponse
        """
        fp = frontend_path / path
        if not fp.exists() or fp.is_dir():
            fp = frontend_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    app.include_router(frontend_router)


def open_gaku_in_browser(url: str) -> None:
    """Opens Gaku in browser after it starts.

    Paramters
    ---------
    url: str
        Url where the Gaku frontend is available.
    """
    max_retries = 300
    retry_delay = 1

    if url == "":
        print("URL not provided, will not open browser")
        return

    if url in ["0.0.0.0", "::/0", "0000:0000:0000:0000:0000:0000:0000:0000/0"]:
        url = "localhost"

    if not url.startswith("http"):
        url = f"http://{url}"

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    logging.info("Gaku is up and running, opening browser")
                    webbrowser.open(url)
                    return
        except URLError as e:
            print(f"Server not ready yet, attempt {attempt}/{max_retries}")
            time.sleep(retry_delay)

    logging.warning("Failed to open browser, Gaku was not ready in time")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gaku - Japanese vocabulary learning program"
    )
    parser.add_argument(
        "--listen", type=str, help="IP address to listen on", default="127.0.0.1"
    )
    parser.add_argument(
        "--port", type=int, help="port to listen to, e.g. 8080", default=8000
    )
    parser.add_argument(
        "-nb",
        "--no-browser",
        action="store_true",
        help="Disable automatic opening of a browser",
        default=False,
    )
    args = parser.parse_args()

    host_url = args.listen
    host_port = args.port

    browser_open_process = multiprocessing.Process(
        target=open_gaku_in_browser, kwargs={"url": f"{host_url}:{host_port}"}
    )
    if not args.no_browser:
        browser_open_process.start()

    uvicorn.run(app, host=host_url, port=host_port)
    browser_open_process.terminate()
