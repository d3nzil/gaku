import { useState } from 'react';

interface TabProps {
    id: string;
    label: string;
    children: React.ReactNode;
}

export const Tabs = ({ tabs }: { tabs: TabProps[] }) => {
    const [selectedTabId, setSelectedTabId] = useState(tabs[0].id);

    const handleTabClick = (tabId: string) => {
        setSelectedTabId(tabId);
    };

    return (
        <div className="tab-container">
            <div className="tab-list">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={tab.id === selectedTabId ? 'active' : ''}
                        onClick={() => handleTabClick(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="tab-content">
                {tabs.map(tab => (
                    <div
                        key={tab.id}
                        style={{ display: (tab.id === selectedTabId ? "block" : "none") }}
                    >
                        {tab.children}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default { Tabs };