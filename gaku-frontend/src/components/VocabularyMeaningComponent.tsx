
import React from 'react';
import MultiInput from './MultiInput';

import { VocabularyMeaningEntry } from '../types/CardTypes';

const VocabularyMeaningComponent: React.FC<{
    meaning: VocabularyMeaningEntry,
    onMeaningChange: (meaning: VocabularyMeaningEntry) => void
}> = ({ meaning, onMeaningChange }) => {

    const handleChange = (field: keyof VocabularyMeaningEntry, value: any) => {
        onMeaningChange({ ...meaning, [field]: value });
    };

    return (
        <div>
            Meaning:<br />
            Part of Speech: <input
                type="text"
                value={meaning.part_of_speech}
                onChange={(e) => handleChange('part_of_speech', e.target.value)}
                style={{ width: '20em' }}
            />
            <br />
            <MultiInput
                values={meaning.meanings}
                onChange={(newMeanings) => handleChange('meanings', newMeanings)}
            />
        </div>
    );
};

export default VocabularyMeaningComponent;