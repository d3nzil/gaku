import React from 'react';
import IMEInput from './IMEInput';
import { AnswerText } from '../types/CardTypes';

interface MultiInputProps {
    values: AnswerText[];
    onChange: (values: AnswerText[]) => void;
    placeholder?: string;
    imeMode?: 'toHiragana' | 'toKatakana' | null;
}

const MultiInput: React.FC<MultiInputProps> = ({ values, onChange, placeholder, imeMode }) => {
    const handleInputChange = (index: number, value: string) => {
        const newValues = [...values];
        newValues[index] = { answer_text: value, required: values[index].required }
        onChange(newValues);
    };

    const addInput = () => {
        onChange([...values, { answer_text: '', required: false }]);
    };

    const removeInput = (index: number) => {
        const newValues = values.filter((_, i) => i !== index);
        onChange(newValues);
    };

    const toggleRequired = (index: number) => {
        const newValues = [...values];
        newValues[index] = { answer_text: values[index].answer_text, required: !values[index].required }
        onChange(newValues);
    };

    return (
        <div style={{ display: 'flex', flexWrap: "wrap", flexDirection: "row", maxWidth: "45em" }}>
            {values.map((value, index) => (
                <div key={index} style={{ display: 'flex', flexDirection: 'row', minWidth: "14em", gap: "0.25em", paddingRight: "0.75em" }}>
                    <IMEInput
                        value={value.answer_text}
                        onChange={(newValue) => handleInputChange(index, newValue)}
                        placeholder={placeholder}
                        initialImeMode={imeMode}
                    />
                    <label>
                        Required: <input type='checkbox' checked={value.required} onChange={() => toggleRequired(index)} />
                    </label>
                    <button onClick={() => removeInput(index)} style={{ backgroundColor: 'pink', color: "darkred" }}>
                        X
                    </button>
                </div>
            ))}
            <button onClick={addInput} style={{ backgroundColor: 'lightgreen', color: "darkgreen" }}>
                +
            </button>
        </div>
    );
};

export default MultiInput;
