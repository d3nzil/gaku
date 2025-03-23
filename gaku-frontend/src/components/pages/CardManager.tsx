import { Tabs } from "../TabView";
import ImportTool from "./ImportTool";
import CardEditor from "./CardEditor";
import SourcesEditor from "./SourcesEditor";

const CardManager = () => {
    return (
        <div style={{ width: "100%", display: "flex" }}>
            <div style={{ flexGrow: 1, textAlign: "center" }}>
                <Tabs tabs={[
                    {
                        id: 'editor',
                        label: 'Card editor',
                        children: <CardEditor />
                    },
                    {
                        id: 'import',
                        label: 'Import',
                        children: <ImportTool />
                    },
                    {
                        id: "export",
                        label: "Export",
                        children: <div>Export</div>
                    },
                    {
                        id: "sources",
                        label: "Sources",
                        children: <SourcesEditor />
                    }
                ]} />
            </div>
        </div>
    );
};

export default CardManager;