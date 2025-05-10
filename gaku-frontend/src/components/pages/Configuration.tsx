import { useState, useEffect } from "react";
import api from "../../services/api";
import { GakuConfig } from '../../types/CardTypes';

const ConfigEditor = () => {
    const [currentConfig, setCurrentConfig] = useState<GakuConfig | null>(null);

    useEffect(() => {
        api.getConfig().then((cfg) => {
            setCurrentConfig(cfg.current)
        })
    }, []);

    const saveConfig = async () => {

        if (currentConfig)
        {
            await api.setConfig(currentConfig);
            api.getConfig().then((cfg) => {
                setCurrentConfig(cfg.current)
            })
        }
    }

    return (
        <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
            <div style={{ maxWidth: "40em" }}>
                <h2 style={{ textAlign: "center" }}>Gaku Configuration</h2>
                {currentConfig ?
                    (<div style={{ flex: "1", display: "flex" }}>
                        <table className="config-table">
                            <tbody>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>Default number of cards to study:</td>
                                    <td style={{ textAlign: "right" }}><input type="number" min={0} value={currentConfig.num_default_cards_to_study} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, num_default_cards_to_study: parseInt(e.target.value) })} /></td>
                                </tr>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>
                                        Number of correct answers required to complete question<br />
                                        <i>Initial, if there was no mistake</i>
                                    </td>
                                    <td style={{ textAlign: "right" }}><input type="number" min={1} value={currentConfig.num_required_answers} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, num_required_answers: parseInt(e.target.value) })} /></td>
                                </tr>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>
                                        Number of correct answers required after mistake<br />
                                        <i>Always set to this value after mistake)</i>
                                    </td>
                                    <td style={{ textAlign: "right" }}><input type="number" min={1} value={currentConfig.num_repeats_after_mistake} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, num_repeats_after_mistake: parseInt(e.target.value) })} /></td>
                                </tr>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>
                                        Generate extra questions<br />
                                        <i>Tests kanji for vocab and radicals for kanji</i>
                                    </td>
                                    <td style={{ textAlign: "right" }}><input type="checkbox" checked={currentConfig.generate_extra_questions} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, generate_extra_questions: e.target.checked })} /></td>
                                </tr>
                                {/* <tr>
                                    <td></td>
                                    <td style={{ textAlign: "right" }}><input /></td>
                                </tr> */}
                                {/* <tr>
                                    <td></td>
                                    <td style={{ textAlign: "right" }}><input /></td>
                                </tr> */}
                            </tbody>
                        </table>
                    </ div>
                    ) : "Loading configuration"}
                <br />
                <i>If test is active, it's settings wont't be affected. You will need to start new test to get the updated settings.</i>
                <br /><br />
                <button onClick={saveConfig}>Save settings</button>
            </div>
        </div >
    )
}

export default ConfigEditor