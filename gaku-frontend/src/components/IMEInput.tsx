import React, { useState } from 'react';
import * as wanakana from 'wanakana';

interface IMEInputProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    /** Pass the desired starting mode, e.g. 'toHiragana' */
    initialImeMode?: 'toHiragana' | 'toKatakana' | null;
    onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>;
}

const IMEInput = React.forwardRef<HTMLInputElement, IMEInputProps>(
    ({ value, onChange, placeholder, initialImeMode: initialMode, onKeyDown }, ref) => {
        // Store the mode in local state, starting with whatever was passed in
        const [imeMode, setImeMode] = useState<'toHiragana' | 'toKatakana' | null>(
            () => initialMode ?? null
        );

        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            let inputValue = e.target.value;
            if (imeMode)
            {
                const convertFunction =
                    imeMode === 'toHiragana' ? wanakana.toKana : wanakana.toKatakana;
                inputValue = convertFunction(inputValue, { IMEMode: true });
            }
            onChange(inputValue);
        };

        const toggleIMEMode = () => {
            setImeMode((prevMode) => {
                if (prevMode === 'toHiragana') return 'toKatakana';
                if (prevMode === 'toKatakana') return null; // fallback to Romaji
                return 'toHiragana'; // default
            });
        };

        const getIMEModeLabel = () => {
            if (imeMode === 'toHiragana') return 'Hiragana';
            if (imeMode === 'toKatakana') return 'Katakana';
            return 'Romaji';
        };

        const getModeSymbol = () => {
            if (imeMode === 'toHiragana') return 'あ';
            if (imeMode === 'toKatakana') return 'ア';
            return 'A';
        }

        return (
            <div style={{ display: 'flex', width: '100%' }} lang="{getLang()}">
                <input
                    ref={ref}
                    type="text"
                    value={value}
                    placeholder={placeholder}
                    onChange={handleChange}
                    onKeyDown={onKeyDown}
                    style={{ flexGrow: 1 }}
                    lang="ja"
                    autoCorrect='off'
                    autoComplete='off'
                    spellCheck="false"
                />
                <input
                    type="button"
                    value={getModeSymbol()}
                    onClick={toggleIMEMode}
                    title={getIMEModeLabel()}
                    tabIndex={-1}
                    style={{ flexShrink: 0 }}
                />
            </div>
        );
    }
);

export default IMEInput;
