import { useState, useEffect } from "react";
import api from "../../services/api";
import { Tabs } from "../TabView";
import ImportTool from "./ImportTool";
import CardEditor from "./CardEditor";
import SourcesEditor from "./SourcesEditor";
import MultiCardEditor from "./multiCardEditor";
import { CardSource } from '../../types/CardTypes';


const CardManager = () => {
    const [sources, setSources] = useState<CardSource[]>([]);

    useEffect(() => {
        const fetchSources = async () => {
            const sources = await api.getSources();
            setSources(sources);
        };
        fetchSources();
    }, []);

    const handleSourcesUpdate = (newSources: CardSource[]) => {
        setSources(newSources);
    };


    return (
        <div style={{ width: "100%", display: "flex" }}>
            <div style={{ flexGrow: 1, textAlign: "center" }}>
                <Tabs tabs={[
                    {
                        id: 'editor',
                        label: 'Card editor',
                        children: <CardEditor
                            sources={sources}
                            onSourcesUpdate={handleSourcesUpdate}
                        />
                    },
                    {
                        id: "multicard",
                        label: "Multi Cards",
                        children: <MultiCardEditor
                            sources={sources}
                            onSourcesUpdate={handleSourcesUpdate}
                        />
                    },
                    {
                        id: 'import',
                        label: 'Import',
                        children: <ImportTool
                            sources={sources}
                            onSourcesUpdate={handleSourcesUpdate}
                        />
                    },
                    {
                        id: "export",
                        label: "Export",
                        children: <div>Export</div>
                    },
                    {
                        id: "sources",
                        label: "Sources",
                        children: <SourcesEditor
                            sources={sources}
                            onSourcesUpdate={handleSourcesUpdate}
                        />
                    }
                ]} />
            </div>
        </div>
    );
};

export default CardManager;