import { useState, useEffect } from 'react';
import api from "../../services/api";
import { CardSource, CardSourcesProps } from '../../types/CardTypes';

const SourcesEditor = (
    { sources, onSourcesUpdate }: CardSourcesProps,
) => {
    // const [sources, setSources] = useState<CardSource[]>([]);

    // sources have: source_id(str), source_name(str), source_section(str)
    const [sourceInput, setSourceInput] = useState<CardSource>({
        source_id: '',
        source_name: '',
        source_section: ''
    });

    useEffect(() => {
        const fetchSources = async () => {
            const sources = await api.getSources();
            onSourcesUpdate(sources);
        };
        document.title = "Gaku - Card Sources";
        fetchSources();
    }, []);

    const addSource = async (sourceData: CardSource) => {
        const response = await api.addSource(sourceData);
        if (response.status === "ok")
        {
            const updatedSources = await api.getSources();
            onSourcesUpdate(updatedSources);
        }
        // Reset the form after adding the source
        setSourceInput({
            source_id: '',
            source_name: '',
            source_section: ''
        });
    };

    const editSource = async (source: CardSource) => {
        const response = await api.updateSource(source);
        if (response.status === "ok")
        {
            const updatedSources = await api.getSources();
            onSourcesUpdate(updatedSources);
        }
    };

    const deleteSource = async (source: CardSource) => {
        const response = await api.deleteSource(source);
        if (response.status === "ok")
        {
            const updatedSources = await api.getSources();
            onSourcesUpdate(updatedSources);
        }
    };

    return (
        <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
            <div style={{ maxWidth: "40em" }}>
                <h2>Sources</h2>
                <table>
                    <tbody>
                        {sources.map((source) => (
                            <tr key={source.source_id}>
                                <td style={{ textAlign: "left", paddingRight: "1em" }}>
                                    {source.source_name} - {source.source_section}
                                </td>
                                <td>
                                    <button onClick={() => deleteSource(source)}>Delete</button>
                                    <button onClick={() => editSource(source)}>Edit</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <h3>Add Source</h3>
                <input
                    type="text"
                    placeholder="Source Name"
                    value={sourceInput.source_name}
                    onChange={(e) => setSourceInput({ ...sourceInput, source_name: e.target.value })}
                />
                <input
                    type="text"
                    placeholder="Source Section"
                    value={sourceInput.source_section}
                    onChange={(e) => setSourceInput({ ...sourceInput, source_section: e.target.value })}
                />
                <button onClick={() => addSource(sourceInput)}>Add Source</button>
            </div>

        </div>
    );
}

export default SourcesEditor;


