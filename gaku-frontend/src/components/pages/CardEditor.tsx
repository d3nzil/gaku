import { useState, useEffect, useRef } from 'react';
import Select from 'react-select';
import api from "../../services/api";
// import Select from 'react-select';
import getEntryComponent from '../cards/CardView';
import { VocabEntry, KanjiEntry, RadicalEntry, QuestionEntry, MultiCardEntry, OnomatopoeiaCard, CardSource, CardType, CardSourcesProps } from '../../types/CardTypes';
import { AnswerType } from '../../types/CardTypes';



type CardTypeOption = { value: CardType, label: string };

const editableTypes = ['VOCABULARY', 'KANJI', 'RADICAL', 'QUESTION', "ONOMATOPOEIA"];
function isEditableType(card: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard): card is VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | OnomatopoeiaCard {
    return editableTypes.includes(card.card_type);
}



const CardEditor = ({ sources }: CardSourcesProps,) => {
    const [cardInput, setCardInput] = useState<VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | OnomatopoeiaCard | null>(null);
    const [cards, setCards] = useState<(VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard)[]>([]);
    const [selectedSources, setSelectedSources] = useState<CardSource[]>([]);
    const [cardType, setCardType] = useState<CardType>(CardType.VOCABULARY);
    // const answerInputRef = useRef(null);
    // const questionInputRef = useRef(null);
    const cardInputRef = useRef(cardInput);
    const numDueCards = useRef(0);
    const [selectedCardTypes, setSelectedCardTypes] = useState<CardType[]>([]);


    const createFilter = () => {
        return {
            card_sources: selectedSources,
            card_types: selectedCardTypes,
            search_text: '',
            start_index: null,
            num_cards: null,
        };
    }

    useEffect(() => {
        cardInputRef.current = cardInput;
    }, [cardInput]);


    useEffect(() => {
        // clear selected sources on sources change
        setSelectedSources([]);
    }, [sources]);

    const addCard = async (cardData: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | OnomatopoeiaCard) => {
        const response = await api.addCard(cardData);
        if (response.status === "ok")
        {
            const updatedCards = await api.getCards();
            setCards(updatedCards);
        }
        return response;
    };

    const editCard = async (updatedCard: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | OnomatopoeiaCard) => {
        const response = await api.updateCard({ card: updatedCard });
        if (response.status === "ok")
        {
            const updatedCards = await api.getCards();
            setCards(updatedCards);
        }
    };

    const saveCard = async () => {
        if (cardInput)
        {
            if (cardInput.card_id)
            {
                await editCard(cardInput);
            } else
            {
                await addCard(cardInput);
            }
            setCardInput(null);
        }
    };

    const newCard = () => {
        setCardInput(createNewCard(cardType));
    };


    useEffect(() => {
        document.title = "Gaku - Card Editor";
        // Fetch all cards from the API when the component loads
        api.getCards().then(setCards);
        // Fetch the number of due cards
        const filter = createFilter();
        api.getNumDueCards(filter).then((num) => {
            numDueCards.current = num;
        });
    }, []); // Empty dependency array to run only once on mount

    useEffect(() => {
        const handleKeyUp = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === 'Enter')
            {
                saveCard();
            }
        };

        document.addEventListener('keyup', handleKeyUp);

        return () => {
            document.removeEventListener('keyup', handleKeyUp);
        };
    }, []); // Empty dependency array

    const deleteCard = async (removedCard: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard) => {
        const response = await api.deleteCard(removedCard);
        if (response.status === "ok")
        {
            const updatedCards = await api.getCards();
            setCards(updatedCards);
        }
    };

    const setCardInputValidated = (card: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard) => {
        if (isEditableType(card))
        {
            setCardInput(card);
        }
    }

    const getSourceLabel = (source_id: string) => {
        const source = sources.find((source) => source.source_id === source_id);
        // label should be source_name + source_section, separated by a dash
        return source ? `${source.source_name} - ${source.source_section}` : source_id;
    }

    return (
        <div style={{ display: "flex", width: '100%', justifyContent: 'center' }}>
            <div style={{ width: '100%', maxWidth: "80em" }}>
                <h2>Card Editor</h2>
                <div style={{ display: 'flex', width: '100%', gap: '1em', flexDirection: 'row', flexWrap: 'wrap' }}>

                    {/* Card Editor Section */}
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: '20em' }}>
                        <div style={{ border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                            <b>Select sources</b>
                            <Select
                                isMulti
                                options={sources.map((source) => ({ value: source, label: getSourceLabel(source.source_id) }))}
                                value={selectedSources.map((source) => ({ value: source, label: getSourceLabel(source.source_id) }))}
                                onChange={(selected) => setSelectedSources(selected.map((source) => source.value))}
                                className='react-select'
                            />
                            <b>Select card types</b>
                            <Select<CardTypeOption, true>
                                isMulti
                                options={[
                                    { value: CardType.KANJI, label: 'Kanji' },
                                    { value: CardType.VOCABULARY, label: 'Vocabulary' },
                                    { value: CardType.RADICAL, label: 'Radical' },
                                    { value: CardType.MULTI_CARD, label: 'Multi Card' },
                                    { value: CardType.QUESTION, label: 'Custom Question' },
                                ]}
                                value={selectedCardTypes.map((type) => ({ value: type, label: type }))}
                                onChange={(selected) => setSelectedCardTypes(selected.map((type) => type.value))}
                                className='react-select'
                            />

                        </div>
                        <div style={{ border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                            <h3 style={{ margin: "0 0", padding: "0.5em 0" }}>Card Editor</h3>
                            <div style={{ padding: "1%" }}>
                                <select value={cardType} onChange={(e) => setCardType(e.target.value as any)} className='react-select'>
                                    <option value="VOCABULARY">Vocabulary</option>
                                    <option value="KANJI">Kanji</option>
                                    <option value="RADICAL">Radical</option>
                                    <option value="ONOMATOPOEIA">Onomatopoeia</option>
                                    <option value="QUESTION">Question</option>
                                </select>
                                <button onClick={newCard}>New Card</button>
                                {cardInput && (
                                    <div>
                                        {getEntryComponent(cardInput, setCardInputValidated)}
                                        <button onClick={saveCard}>Save Card</button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div style={{ flex: 1, maxHeight: '90vh', minWidth: "20em", overflowY: 'auto', border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                        <h3 style={{ margin: "0 0", padding: "0.5em 0" }}>All Cards</h3>
                        {/* <br /> */}
                        <ul style={{ listStyleType: "none", padding: 0 }}>
                            {cards.map((card) => (
                                <li key={card.card_id} style={{ paddingLeft: "1%" }}>
                                    {getEntryComponent(card, () => { })}

                                    {isEditableType(card) &&
                                        <button onClick={() => setCardInput(card)}>Edit</button>
                                    }
                                    <button onClick={() => deleteCard(card)}>Delete</button>
                                    <br /><br />
                                    <hr />
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div >
        </div >
    );
};

export default CardEditor;

// Helper function to create a new card based on the selected type
const createNewCard = (type: CardType) => {
    switch (type)
    {
        case CardType.VOCABULARY:
            return {
                card_id: '',
                card_type: 'VOCABULARY',
                custom_questions: [],
                note: "",
                hint: "",
                dictionary_id: 0,
                writing: '',
                reading_type: AnswerType.HIRAGANA,
                readings: [],
                meanings: [],
            } as VocabEntry;
        case CardType.KANJI:
            return {
                card_id: '',
                dictionary_id: null,
                card_type: 'KANJI',
                custom_questions: [],
                note: "",
                hint: "",
                writing: '',
                on_readings: [],
                kun_readings: [],
                meanings: [],
                radical_id: 0,
            } as KanjiEntry;
        case CardType.RADICAL:
            return {
                card_id: '',
                card_type: 'RADICAL',
                custom_questions: [],
                note: "",
                hint: "",
                writing: '',
                meanings: [],
                reading: '',
                dictionary_id: 0,
            } as RadicalEntry;
        case CardType.QUESTION:
            return {
                card_id: '',
                card_type: 'QUESTION',
                note: "",
                hint: "",
                question: '',
                answers: []
            } as QuestionEntry;
        case CardType.ONOMATOPOEIA:
            return {
                card_id: '',
                card_type: "ONOMATOPOEIA",
                note: "",
                hint: "",
                writing: '',
                kana_writing: [""],
                definitions: [{ meaning: { required: false, answer_text: "" }, equivalent: [{ required: false, answer_text: "" }] }]

            } as OnomatopoeiaCard;
        default:
            return null;
    }
};
