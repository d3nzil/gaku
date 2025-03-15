import { Link } from 'react-router-dom';
import { useCommonState } from './CommonState';
import { useTheme, ThemeType } from './Theme';


const Navigation = () => {
    const { currentThemeType, setCurrentTheme } = useTheme();

    const toggleTheme = () => {
        const newTheme = currentThemeType === ThemeType.LIGHT ? ThemeType.DARK : ThemeType.LIGHT;
        setCurrentTheme(newTheme);
    }

    const context = useCommonState();
    if (!context)
    {
        throw new Error('CommonStateProvider not found');
    }

    return (
        <nav>
            <div style={{ width: "100%", display: "flex" }}>
                {/* <div> */}
                <div style={{ flexGrow: 1, textAlign: "center" }}>
                    <img src="/icon.svg" alt="Gaku" style={{ height: "1em", alignSelf: "flex-start" }} />
                    <b> </b>
                    {currentThemeType === ThemeType.LIGHT ? (
                        <a href="#" onClick={toggleTheme}>🌞</a>
                    ) : (
                        <a href="#" onClick={toggleTheme}>🌙</a>
                    )}

                    <b> </b>
                    <a href='./documentation/index.html' target='_blank' rel='noopener noreferrer'>Docs</a>
                    <b> </b>
                    <Link to="/cards">Cards</Link>
                    <b> | </b>
                    <Link to="/multi">Multi Cards</Link>
                    <b> | </b>
                    <Link to="/source">Sources</Link>
                    <b> | </b>
                    <Link to="/import">Import</Link>
                    <b> | </b>
                    <Link to="/">Select Test</Link>
                    {context.testSessionActive && (<>
                        <b> | </b>
                        <Link to="/test">Continue Test</Link>
                    </>)}
                </div>
            </div>
            <br />
        </nav >
    );
};

export default Navigation;