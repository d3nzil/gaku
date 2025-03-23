import axios from 'axios';
import { VocabEntry, KanjiEntry, RadicalEntry, QuestionEntry, TestAnswer, CardSource, NextCardMessage, TestStatusMessage, GeneratedImports, CardFilter, MultiCardEntry, StartTestRequest, TestResults, OnomatopoeiaCard, AnswerCheckResponse, UpdateCardRequest } from '../types/CardTypes';

const apiUrl = import.meta.env.VITE_APP_API_URL as string || "http://localhost:8000/api";

// card editor API methods
const getCards = (): Promise<(VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard)[]> =>
    axios.get(`${apiUrl}/cards`).then((response) => response.data);

const addCard = (card: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard): Promise<any> =>
    axios.post(`${apiUrl}/cards/add`, card).then((response) => response.data);

const updateCard = (update_request: UpdateCardRequest): Promise<any> =>
    axios.post(`${apiUrl}/cards/update`, update_request).then((response) => response.data);

const deleteCard = (card: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard): Promise<any> =>
    axios.post(`${apiUrl}/cards/delete`, card).then((response) => response.data);

const getCardsByText = (filter: CardFilter): Promise<(VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard)[]> =>
    axios.post(`${apiUrl}/cards/get_by_text`, filter).then((response) => response.data);

// card source API methods
const getSources = (): Promise<CardSource[]> =>
    axios.get(`${apiUrl}/sources`).then((response) => response.data);

const addSource = (source: CardSource): Promise<{ status: string; source_id: string }> =>
    axios.post(`${apiUrl}/sources/add`, source).then((response) => response.data);

const updateSource = (source: CardSource): Promise<{ status: string }> =>
    axios.post(`${apiUrl}/sources/update`, source).then((response) => response.data);

const deleteSource = (source: CardSource): Promise<{ status: string }> =>
    axios.post(`${apiUrl}/sources/delete`, source).then((response) => response.data);

// card source link API methods
const addCardSourceLink = (card_id: string, source_id: string): Promise<{ status: string }> =>
    axios.post(`${apiUrl}/cards/add_source_link`, { card_id, source_id }).then((response) => response.data);

const deleteAllCardSourceLinks = (card_id: string): Promise<{ status: string }> =>
    axios.post(`${apiUrl}/cards/delete_all_source_links`, { card_id }).then((response) => response.data);

const deleteCardSourceLink = (card_id: string, source_id: string): Promise<{ status: string }> =>
    axios.post(`${apiUrl}/cards/delete_source_link`, { card_id, source_id }).then((response) => response.data);

// card testing API methods
const startTestAll = (request: StartTestRequest) =>
    axios.post(`${apiUrl}/test/start`, request).then((response) => response.data);
const startTestNew = (request: StartTestRequest) =>
    axios.post(`${apiUrl}/test/start_new`, request).then((response) => response.data);
const getNumNewCards = (request: CardFilter) => axios.post(`${apiUrl}/test/num_new`, request).then((response) => response.data);
const startTestStudied = (request: StartTestRequest) =>
    axios.post(`${apiUrl}/test/start_studied`, request).then((response) => response.data);
const getNumStudiedCards = (request: CardFilter): Promise<number> =>
    axios.post(`${apiUrl}/test/num_studied`, request).then((response) => response.data);
const getNumAnyStateCards = (request: CardFilter) => axios.post(`${apiUrl}/test/num_any_state`, request).then((response) => response.data);
const startTestDue = (request: StartTestRequest) =>
    axios.post(`${apiUrl}/test/start_due`, request).then((response) => response.data);
const getNumDueCards = (request: CardFilter) => axios.post(`${apiUrl}/test/num_due`, request).then((response) => response.data);
const getNumRecentMistakesSince = (filter: CardFilter, time_since: number) => axios.post(`${apiUrl}/test/num_recent_mistakes_since`, { filter, time_since }).then((response) => response.data);
const startTestRecentMistakes = (start_request: StartTestRequest, time_since: number) => axios.post(`${apiUrl}/test/start_recent_mistakes`, { start_request, time_since }).then((response) => response.data);
const getNextCard = (): Promise<NextCardMessage> => axios.get(`${apiUrl}/test/next`).then((response) => response.data);
const checkAnswer = (answer: TestAnswer): Promise<AnswerCheckResponse> => axios.post(`${apiUrl}/test/check_answer`, { answer }).then((response) => response.data);
const submitAnswer = (answer: TestAnswer): Promise<AnswerCheckResponse> => axios.post(`${apiUrl}/test/answer_question`, { answer }).then((response) => response.data);
const getTestResults = (): Promise<TestResults> => axios.get(`${apiUrl}/test/results`).then((response) => response.data);
const getTestStatus = (): Promise<TestStatusMessage> => axios.get(`${apiUrl}/test/status`).then((response) => response.data);
const wrapUpTest = () => axios.get(`${apiUrl}/test/wrap_up`).then((response) => response.data);
const getSessionStatus = (): Promise<boolean> => axios.get(`${apiUrl}/test/session_active`).then((response) => response.data.session_active);
const markCorrect = (answer: TestAnswer) => axios.post(`${apiUrl}/test/mark_correct`, { answer }).then((response) => response.data);
const markMistake = (answer: TestAnswer) => axios.post(`${apiUrl}/test/mark_mistake`, { answer }).then((response) => response.data);
const practiceFailedCards = () => axios.post(`${apiUrl}/test/practice_failed_cards`).then((response) => response.data);
const practiceAllCards = () => axios.post(`${apiUrl}/test/practice_all_cards`).then((response) => response.data);
const isPractice = () => axios.get(`${apiUrl}/test/is_practice`).then((response) => response.data);


// vocabulary import API methods
const generateImportVocabNew = (vocab: string): Promise<GeneratedImports> => axios.post(`${apiUrl}/vocab/generate_vocab_import`, { vocab }).then((response) => response.data);
const importCards = (cards: GeneratedImports, sources: CardSource[]) => axios.post(`${apiUrl}/vocab/import_cards`, { cards, sources }).then((response) => response.data);

// stats
const getNumDueStats = (): Promise<{ [key: number]: number }> => axios.get(`${apiUrl}/stats/num_due`).then((response) => response.data);
const getNumRecentMistakes = (): Promise<{ [key: number]: number }> => axios.get(`${apiUrl}/stats/num_recent_mistakes`).then((response) => response.data);

export default {
    getCards,
    addCard,
    updateCard,
    deleteCard,
    getCardsByText,
    startTestAll,
    startTestNew,
    startTestStudied,
    getNumStudiedCards,
    startTestDue,
    startTestRecentMistakes,
    getNumRecentMistakesSince,
    getNumNewCards,
    getNumAnyStateCards,
    getNumDueCards,
    getNextCard,
    checkAnswer,
    submitAnswer,
    getTestResults,
    getTestStatus,
    getSources,
    addSource,
    updateSource,
    deleteSource,
    addCardSourceLink,
    deleteAllCardSourceLinks,
    deleteCardSourceLink,
    wrapUpTest,
    getSessionStatus,
    markCorrect,
    markMistake,
    generateImportVocabNew,
    importCardsNew: importCards,
    getNumDueStats,
    getNumRecentMistakes,
    practiceFailedCards,
    practiceAllCards,
    isPractice,
};