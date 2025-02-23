import React, { useState, useEffect } from 'react';
import api from "../../services/api";
import Select from 'react-select';
import getEntryComponent from '../cards/CardView';

import { VocabEntry, KanjiEntry, RadicalEntry, QuestionEntry, CardSource, GeneratedImports, ImportItem, MultiCardEntry } from '../../types/CardTypes';


const ImportTool = () => {
    const [importText, setImportText] = useState('');
    const [allSources, setAllSources] = useState<CardSource[]>([]);
    const [selectedSources, setSelectedSources] = useState<CardSource[]>([]);
    const [generatedImports, setGeneratedImports] = useState<GeneratedImports | null>(null);
    const [importResult, setImportResult] = useState<string | null>(null);
    const [showExistingCards, setShowExistingCards] = useState<boolean>(true);

    // initialize the import tool
    useEffect(() => {
        document.title = "Gaku - Import Tool";
        api.getSources().then(setAllSources);
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file)
        {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (e.target?.result)
                {
                    setImportText(e.target.result as string);
                }
            };
            reader.readAsText(file);
        }
    }

    const generateImports = () => {
        // clear previous imports
        setGeneratedImports(null);
        // generate imports
        api.generateImportVocabNew(importText).then(setGeneratedImports);
    }

    const clearImports = () => {
        setGeneratedImports(null);
        setImportText('');
    }

    const handleEntryChange = (
        updatedEntry: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry
    ) => {
        if (generatedImports)
        {
            setGeneratedImports({
                ...generatedImports,
                generated_cards: {
                    ...generatedImports.generated_cards,
                    [updatedEntry.card_id]: updatedEntry,
                },
            });
        }
    };

    const isNewCard = (card_id: string) => {
        return generatedImports?.new_card_ids.includes(card_id);
    }

    const deleteImportItem = (item_id: string) => {
        // TODO: for kanji and radicals we need to show confirmation dialog
        // as this will remove this card from the whole import
        // for vocab we can just remove it as deleting it doesn't affect the sub items

        const deleteItem = (item: ImportItem, item_id: string): ImportItem | null => {
            if (item.item_id === item_id)
            {
                return null; // Delete this item
            } else
            {
                item.sub_items = item.sub_items
                    .map(subItem => deleteItem(subItem, item_id))
                    .filter(subItem => subItem !== null) as ImportItem[];
                return item;
            }
        };

        if (generatedImports)
        {
            const newImportItems = generatedImports.import_items
                .map(item => deleteItem(item, item_id))
                .filter(item => item !== null) as ImportItem[];
            setGeneratedImports({ ...generatedImports, import_items: newImportItems });
        }
    }

    const displayImportItem = (item: ImportItem) => {
        const itemCard = generatedImports?.generated_cards[item.item_id];
        if (itemCard === undefined) { return null; }

        if (!showExistingCards && !isNewCard(item.item_id)) { return null; }

        return (
            <div key={item.item_id} style={{ paddingTop: "1em" }}>
                <div style={{ display: 'flex', flexDirection: 'row', gap: "1em" }}>
                    {/* show if it is new card or existing one */}
                    {isNewCard(item.item_id) && <div style={{ color: 'red' }}>New card</div> || <div style={{ color: 'green' }}>Existing card</div>}
                    {/* delete */}
                    <button onClick={() => deleteImportItem(item.item_id)}>Delete</button>
                    {/* show the card */}
                </div>
                {getEntryComponent(itemCard, handleEntryChange)}
                <hr />
                <div style={{ display: "flex", flexDirection: "row" }}>
                    <div style={{ backgroundColor: 'lightgrey', width: "1em" }} />
                    <div style={{ marginLeft: '1em' }}>
                        {item.sub_items.map(subItem => displayImportItem(subItem))}
                    </div>
                </div>
            </div>
        );
    }

    const importCards = () => {
        if (!generatedImports) { return; }
        api.importCardsNew(generatedImports, selectedSources).then((response) => {
            if (response.status === "ok")
            {
                setImportResult("Import successful");
                // clear the generated imports
                clearImports();
            } else
            {
                setImportResult("Import failed: " + response.error);
            }
        }
        );
    }

    const getSourceLabel = (source_id: string) => {
        const source = allSources.find((source) => source.source_id === source_id);
        // label should be source_name + source_section, separated by a dash
        return source ? `${source.source_name} - ${source.source_section}` : source_id;
    }


    // render the import tool
    return (
        <div>
            <div style={{ flexDirection: 'row', display: 'flex' }}>

                {/* text import section */}
                <div style={{ width: "20em" }}>
                    <h2>Vocabulary import</h2>
                    <input type="file" accept='.txt' onChange={handleFileChange} />
                    <br /><br />
                    <textarea
                        style={{ height: '30em' }}
                        value={importText}
                        onChange={(e) => setImportText(e.target.value)}
                        lang='ja'
                    />
                    <br />
                    <br />

                    <button onClick={generateImports} >Generate imports</button>

                    {generatedImports && (
                        <>
                            <br /><br />
                            {/* show existing cards toggle */}
                            <label>
                                <input type="checkbox" checked={showExistingCards} onChange={() => setShowExistingCards(!showExistingCards)} />
                                Show existing cards
                            </label>
                            <br />
                            <button onClick={importCards}>Import cards</button>
                            <br /><br />
                            {/* show the error log if present */}
                            {generatedImports.errors && (
                                <>
                                    <h3>Import generation errors:</h3>
                                    <textarea
                                        style={{ height: '10em', width: '25em' }}
                                        value={generatedImports.errors.join('\n')}
                                        readOnly
                                    />
                                </>
                            )}
                        </>
                    )}
                </div>

                {/* generated imports section */}
                <div style={{ paddingLeft: "1em" }}>
                    <h2>Generated imports</h2>
                    <h3>Selected sources</h3>
                    <Select
                        options={allSources.map((source) => ({ value: source.source_id, label: getSourceLabel(source.source_id) }))}
                        isMulti
                        onChange={(selectedOptions) => setSelectedSources(selectedOptions.map((option) => allSources.find((source) => source.source_id === option.value)!))}
                        className='react-select'
                    />
                    <br />
                    {generatedImports && (
                        <>
                            {generatedImports.import_items.map(displayImportItem)}
                        </>
                    )}
                </div>

                {/* import result section */}
                {importResult && (
                    <div style={{ paddingLeft: "1em" }}>
                        <h2>Import result</h2>
                        {importResult}
                    </div>
                )}


            </div>

        </div>
    );
}

export default ImportTool;