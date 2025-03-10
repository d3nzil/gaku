import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from "../../services/api";
import IMEInput from '../IMEInput';
import { NextCardMessage, VocabEntry, KanjiEntry, RadicalEntry, QuestionEntry, TestQuestion, OnomatopoeiaCard, AnswerText, MultiCardEntry } from '../../types/CardTypes';
import { getEntryComponent } from '../cards/CardView';
import { useCommonState } from '../CommonState';

const TestFlashcards = () => {
    const context = useCommonState();
    if (!context)
    {
        throw new Error('useCommonState must be used within a CommonStateProvider');
    }

    const [currentQuestion, setCurrentCard] = useState<TestQuestion | null>(null);
    const [answers, setAnswers] = useState<{ [key: string]: string }>({});
    // answer order is used to keep track of the order of the answers using answer ids
    const [answerOrder, setAnswerOrder] = useState<string[]>([]);
    const navigate = useNavigate();
    const [testStatus, setTestStatus] = useState({ questions_completed: 0, questions_total: 0, cards_completed: 0, cards_total: 0 });
    const [checkResult, setCheckResult] = useState<boolean | null>(null);
    const [showHint, setShowHint] = useState(false);
    const [showAnswer, setShowAnswer] = useState(false);
    const [isPractice, setIsPractice] = useState<boolean | null>(null);

    // Refs for input fields
    const inputRefs = useRef<HTMLInputElement[]>([]);
    const submitInputRef = useRef<HTMLInputElement>(null);

    // Add state for available and selected card sources
    const [receivedCard, setReceivedCard] = useState<VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | OnomatopoeiaCard | MultiCardEntry | null>(null);
    const [showCardInfo, setShowCardInfo] = useState(false);
    const { updateTestSessionStatus } = context;

    // header
    const questionHeaderRef = useRef<HTMLStyleElement | null>(null);

    // update test session status and fetch next card on component mount
    useEffect(() => {
        const fetchSessionStatus = async () => {
            const active = await updateTestSessionStatus();
            if (!active) 
            {
                navigate('/select-test');
            }
            fetchNextCard();
        };
        document.title = "Gaku - Test Flashcards";
        fetchSessionStatus();
        api.isPractice().then((practice) => {
            setIsPractice(practice);
        });
        if (questionHeaderRef.current)
        {
            questionHeaderRef.current.scrollIntoView();
        }
    }, []);

    useEffect(() => {
        if (currentQuestion)
        {
            inputRefs.current = [];
            setAnswers({});
            setAnswerOrder(currentQuestion.answers.map((answer_group) => answer_group.answers.map((answer) => answer.answer_id)).flat());
            inputRefs.current[0]?.focus();
            setTimeout(() => {
                inputRefs.current[0]?.focus();
            }, 1);
        }
    }, [currentQuestion]);

    const getAnswerIndex = (answer_id: string) => {
        return answerOrder.indexOf(answer_id);
    }

    const fetchTestStatus = async () => {
        const status = await api.getTestStatus();
        setTestStatus(status);
    };

    const fetchNextCard = async () => {
        setShowCardInfo(false);
        setCheckResult(null);
        setShowAnswer(false);
        const cardMessage: NextCardMessage = await api.getNextCard();
        if (cardMessage && cardMessage.test_card)
        {
            setCurrentCard(cardMessage.next_question);
            setReceivedCard(cardMessage.test_card);
        } else
        {
            // update common state to reflect that the test is over
            await context.updateTestSessionStatus();
            navigate('/results');
        }
        fetchTestStatus();
    };

    // const wrapUpTest = async () => {
    //     await api.wrapUpTest();
    //     await context.updateTestSessionStatus();
    //     navigate('/results');
    // };

    const checkAnswerIsCorrect = async () => {
        const result = await api.checkAnswer(answers);
        setCheckResult(result.answer_is_correct);
        setShowAnswer(!result.answer_is_correct);
    };

    const handleInputChange = (id: string, value: string) => {
        setAnswers(prev => ({ ...prev, [id]: value }));
    };

    const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
        if (e.key === 'Enter')
        {
            if (e.ctrlKey)
            {
                e.preventDefault();
                submitAnswer();
            } else
            {
                e.preventDefault();
                if (index + 1 < inputRefs.current.length)
                {
                    inputRefs.current[index + 1]?.focus();
                } else
                {
                    submitInputRef.current?.focus();
                    checkAnswerIsCorrect();
                }
            }
        }
    };


    const toggleHint = () => {
        setShowHint(!showHint);
    }

    const getAnswerDisplay = (answer: AnswerText) => {
        if (answer.required)
        {
            return (<><b>{answer.answer_text}</b></>)
        } else
        {
            return <>{answer.answer_text}</>
        }
    };


    useEffect(() => {
        const handleShortcut = (e: KeyboardEvent) => {

            // ctrl-i was not working, shows page info in firefox
            // ctrl-t also not working - new tab
            // ctrl-d not working - bookmark
            // ctrl-m not working - mute tab in firefox
            // f3 not working - find
            if (e.key === 'F4')
            {
                e.preventDefault();
                setShowCardInfo(!showCardInfo);
            }
            // ctrl+h toggle hint - not working - opens history sidebar in firefox
            if (e.key === 'F2')
            {
                e.preventDefault();
                toggleHint();
            }
            // ctrl+enter to submit
            if (e.ctrlKey && e.key === 'Enter')
            {
                e.preventDefault();
                submitAnswer();
            }
            // if the checkResult is not null, use F3 to toggle show answer
            if (checkResult !== null && e.key === 'F3')
            {
                e.preventDefault();
                toggleShowAnswer();
            }
        };
        window.addEventListener('keydown', handleShortcut);

        return () => {
            window.removeEventListener('keydown', handleShortcut);
        };
    }, [toggleHint, showCardInfo]);

    // const handleShortcut = (e: KeyboardEvent) => {

    //     // ctrl-i was not working, shows page info in firefox
    //     // ctrl-t also not working - new tab
    //     // ctrl-d not working - bookmark
    //     // ctrl-m not working - mute tab in firefox
    //     // f3 not working - find
    //     if (e.key === 'F4')
    //     {
    //         e.preventDefault();
    //         setShowCardInfo(!showCardInfo);
    //     }
    //     // ctrl+h toggle hint - not working - opens history sidebar in firefox
    //     if (e.key === 'F2')
    //     {
    //         e.preventDefault();
    //         toggleHint();
    //     }
    // };

    const submitAnswer = async () => {
        // defocus the submit button to prevent accidental double submission
        // submitButtonRef.current?.blur();
        submitInputRef.current?.blur();

        // if check is null, check the answer before submitting
        if (checkResult === null)
        {
            checkAnswerIsCorrect();
            return;
        }

        // if (result.answer_is_correct)
        // {
        fetchTestStatus();
        fetchNextCard();
        // } else
        // {
        //     setTimeout(() => {
        //         nextCardRef.current?.focus();
        //     }, 0);
        // }
    };

    const markCorrect = async () => {
        await api.markCorrect(answers);
        fetchTestStatus();
        fetchNextCard();
    };

    const markMistake = async () => {
        await api.markMistake(answers);
        fetchTestStatus();
        fetchNextCard();
    }

    const toggleShowAnswer = () => {
        setShowAnswer(!showAnswer);
    };


    return (
        <div style={{ display: 'flex', justifyContent: 'center', width: "100%" }}>

            <div style={{ display: 'flex', alignContent: "flex-start", flexDirection: "column", width: "100%", maxWidth: "40em" }}>
                <div style={{ width: "100%" }}>
                    <div style={{ fontSize: "0.85em" }}>
                        <p>{isPractice === true ? ("Practice") : ("Test")}: {testStatus.cards_completed}/{testStatus.cards_total} cards completed ({testStatus.questions_completed}/{testStatus.questions_total} questions).
                            <a href="#" onClick={toggleHint}> Hint {showHint ? "on" : "off"}</a>
                        </p>
                    </div>
                    {/* current question */}
                    {currentQuestion ? (
                        <div>
                            <b ref={questionHeaderRef}>{currentQuestion.header}</b><br />
                            <p style={{ fontSize: "2.5em", margin: "0" }} lang='ja'>{currentQuestion.question}</p>
                            {/* <br /> */}
                            {showHint && <div style={{ maxWidth: "20em", paddingBottom: "0.5em" }}> {currentQuestion.hint}</div>}
                            {/* <br /> */}

                            <div style={{ display: 'flex', flexDirection: 'row', gap: "0.25em", flexWrap: "wrap", width: "100%", }}>
                                {currentQuestion.answers.map((answer_group) => {
                                    return (
                                        <div style={{ flex: "1", minWidth: "15em", border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em" }}>
                                            {answer_group.header && <div style={{ fontSize: "1.25em", paddingTop: "0.5em" }}>{answer_group.header}</div>}
                                            {answer_group.answers.map((answer) => (
                                                <div key={answer.answer_id} style={{ fontSize: "1.25em", paddingBottom: "0.5em" }}>
                                                    <div style={{ paddingBottom: "0.25em" }}>{answer.header}{answer.header_num_questions}:</div>
                                                    <IMEInput
                                                        ref={(el) => {
                                                            if (el)
                                                            {
                                                                inputRefs.current[getAnswerIndex(answer.answer_id)] = el;
                                                            }
                                                        }}
                                                        value={answers[answer.answer_id] || ''}
                                                        onChange={(value) => handleInputChange(answer.answer_id, value)}
                                                        initialImeMode={
                                                            answer.answer_type === 'HIRAGANA' ? 'toHiragana' :
                                                                answer.answer_type === 'KATAKANA' ? 'toKatakana' :
                                                                    null
                                                        }
                                                        onKeyDown={(e) => handleKeyDown(e, getAnswerIndex(answer.answer_id))}
                                                    />
                                                    {/* <br /> */}
                                                </div>
                                            ))}
                                        </div>
                                    )
                                })}
                            </div>
                            {/* invisible input field for submitting on phone without hiding keyboard*/}
                            <input
                                ref={submitInputRef}
                                style={{ position: 'absolute', left: '-99999px' }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter')
                                    {
                                        submitAnswer();
                                    }
                                }}
                            />
                            {/* <button ref={submitButtonRef} onClick={submitAnswer}>Submit Answer</button> */}

                            {checkResult === null && (
                                <div style={{ display: 'flex', gap: "1em" }}>
                                    <button onClick={checkAnswerIsCorrect}>Check answer</button>
                                </div>
                            )}

                            {checkResult === false && (
                                <div>
                                    <p className='incorrect-answer' style={{ height: "2em", textAlign: "center", paddingTop: "0.75em" }} >Wrong answer</p>
                                    <div style={{ display: 'flex', gap: "1em" }}>
                                        <button onClick={markCorrect} >Mark as correct</button>
                                        <button onClick={checkAnswerIsCorrect}>Recheck</button>
                                        <button onClick={submitAnswer}>Try again</button>
                                    </div>
                                </div>
                            )}
                            {checkResult === true && (
                                <div>
                                    <p className='correct-answer' style={{ height: "2em", textAlign: "center", paddingTop: "0.75em" }} >Correct answer</p>
                                    <div style={{ display: 'flex', gap: "1em" }}>
                                        <button onClick={markMistake}>Mark as mistake</button>
                                        <button onClick={toggleShowAnswer}>{showAnswer && "Hide Answer" || "Show Answer"} </button>
                                        <button onClick={submitAnswer}>Next Card</button>
                                    </div>
                                </div>
                            )
                            }
                            <br />
                            {showAnswer && (
                                <div style={{ border: "1px" }} lang='ja'>
                                    <div style={{ padding: "0.2em", border: "1px solid #888", width: "100%" }}>
                                        Correct answers (required answers and in <b>bold</b>):
                                        {currentQuestion.answers.map((answer_group) => {
                                            return (
                                                <div>
                                                    {answer_group.header && <div style={{ fontSize: "1.25em", padding: "0" }} >{answer_group.header}:</div>}
                                                    {answer_group.answers.map((answer) => (
                                                        <div key={answer.answer_id}>
                                                            <div style={{ fontSize: "0.85em", paddingTop: "0em" }} >{answer.header}:</div>
                                                            <div>
                                                                {answer.answers.map((item, index) => (
                                                                    <React.Fragment key={index}>
                                                                        {getAnswerDisplay(item)}
                                                                        {index < answer.answers.length - 1 && "; "}
                                                                    </React.Fragment>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    ))}
                                                    <br />
                                                </div>
                                            )
                                        })}


                                    </div>
                                </div>
                            )}

                        </div>
                    ) : (
                        <p>Loading...</p>
                    )}
                    {/* <br /> */}
                    {/* <br /> */}
                    {/* <button onClick={wrapUpTest}>Wrap Up Test</button> */}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', paddingTop: "1em" }}>
                    <div>
                        {/* current test card */}
                        <button onClick={() => setShowCardInfo(!showCardInfo)} title='F4 - show/hide card info'>
                            {showCardInfo ? 'Hide Card Info' : 'Show Card Info'}
                        </button>

                        {showCardInfo && receivedCard && (
                            <div
                                style={{
                                    border: '1px solid #ccc',
                                    padding: '10px'
                                }}
                            >
                                {getEntryComponent(receivedCard, () => { })}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div >
    );
};

export default TestFlashcards;
