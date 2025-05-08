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
                        <table>
                            <tbody>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>Default number of cards to study:</td>
                                    <td style={{ textAlign: "right" }}><input type="number" min={0} value={currentConfig.num_default_cards_to_study} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, num_default_cards_to_study: parseInt(e.target.value) })} /></td>
                                </tr>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>
                                        Number of correct answers required to complete question<br />
                                        (Initial, if there was no mistake)
                                    </td>
                                    <td style={{ textAlign: "right" }}><input type="number" min={1} value={currentConfig.num_required_answers} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, num_required_answers: parseInt(e.target.value) })} /></td>
                                </tr>
                                <tr>
                                    <td style={{ paddingRight: "1em" }}>
                                        Number of correct answers required after mistake<br />
                                        (Always set to this value after mistake)
                                    </td>
                                    <td style={{ textAlign: "right" }}><input type="number" min={1} value={currentConfig.num_repeats_after_mistake} style={{ width: "3em" }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentConfig({ ...currentConfig, num_repeats_after_mistake: parseInt(e.target.value) })} /></td>
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
                <button onClick={saveConfig}>Save settings</button>
            </div>
        </div >
    )
}

export default ConfigEditor