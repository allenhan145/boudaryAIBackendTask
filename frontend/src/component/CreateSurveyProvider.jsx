import React, { createContext, useContext, useState, useCallback } from "react";

const CreateSurveyContext = createContext();

export const CreateSurveyProviderMock = ({ children }) => {
  const [surveyTitle, setSurveyTitle] = useState("My Survey Title");
  const [surveyDescription, setSurveyDescription] = useState("This is a sample survey.");
  const [questions, setQuestions] = useState([]);
  const [dupList, setDupList] = useState([]);
  const [isAddingOption, setIsAddingOption] = useState(false);
  const defaultQuestionType = "shortAnswer";

  const addNewQuestion = (type = defaultQuestionType) => {
    const newQuestion = {
      id: Date.now() + Math.random(),
      type,
      title: "",
      saved: false,
      options: type === "multipleChoice" || type === "singleChoice" ? [
        { id: Date.now() + Math.random(), text: "" },
        { id: Date.now() + Math.random() + 1, text: "" }
      ] : []
    };
    setQuestions((prev) => [...prev, newQuestion]);
  };

  const handleDeleteQuestion = (index) => {
    setQuestions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAddOption = useCallback((questionIndex) => {
    if (isAddingOption) {
      return;
    }

    setIsAddingOption(true);

    setQuestions((prev) => {
      const newQuestions = [...prev];
      if (!newQuestions[questionIndex].options) {
        newQuestions[questionIndex].options = [];
      }
      const newOption = {
        id: Date.now() + Math.random(),
        text: "",
      };
      newQuestions[questionIndex].options.push(newOption);

      // Reset the flag after the state update
      setTimeout(() => {
        setIsAddingOption(false);
      }, 0);

      return newQuestions;
    });
  }, [isAddingOption]);

  const handleTitleChange = (questionIndex, title) => {
    setQuestions((prev) => {
      const newQuestions = [...prev];
      newQuestions[questionIndex].title = title;
      return newQuestions;
    });
  };

  const handleQuestionTypeChange = (questionIndex, type) => {
    setQuestions((prev) => {
      const newQuestions = [...prev];
      newQuestions[questionIndex].type = type;
      
      // Ensure multiple choice and single choice questions have at least 2 empty options
      if (type === "multipleChoice" || type === "singleChoice") {
        if (!newQuestions[questionIndex].options || newQuestions[questionIndex].options.length < 2) {
          newQuestions[questionIndex].options = [
            { id: Date.now() + Math.random(), text: "" },
            { id: Date.now() + Math.random() + 1, text: "" }
          ];
        }
      } else {
        // Clear options for non-choice questions
        newQuestions[questionIndex].options = [];
      }
      
      return newQuestions;
    });
  };

  const handleOptionChange = (questionIndex, optionIndex, value) => {
    setQuestions((prev) => {
      const newQuestions = [...prev];
      if (newQuestions[questionIndex].options) {
        newQuestions[questionIndex].options[optionIndex].text = value;
      }
      return newQuestions;
    });
  };

  const handleSaveQuestion = (questionIndex) => {
    setQuestions((prev) => {
      const newQuestions = [...prev];
      newQuestions[questionIndex].saved = true;
      return newQuestions;
    });
  };

  const handleEditQuestion = (questionIndex) => {
    setQuestions((prev) => {
      const newQuestions = [...prev];
      newQuestions[questionIndex].saved = false;
      return newQuestions;
    });
  };

  const handleDuplicate = (questionIndex) => {
    const questionToDuplicate = questions[questionIndex];
    const duplicatedQuestion = {
      ...questionToDuplicate,
      id: Date.now(),
      saved: false,
    };
    setQuestions((prev) => [...prev, duplicatedQuestion]);
  };

  const handleDeleteOption = (questionIndex, optionId) => {
    setQuestions((prev) => {
      const newQuestions = [...prev];
      if (newQuestions[questionIndex].options) {
        const optionIndex = newQuestions[questionIndex].options.findIndex(option => option.id === optionId);
        if (optionIndex !== -1) {
          newQuestions[questionIndex].options.splice(optionIndex, 1);
        }
      }
      return newQuestions;
    });
  };

  const onDragEnd = (result) => {
    if (!result.destination) {
      return;
    }
    const items = Array.from(questions);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setQuestions(items);
  };

  const handleCreateSurvey = () => {};

  return (
    <CreateSurveyContext.Provider
      value={{
        surveyTitle,
        setSurveyTitle,
        surveyDescription,
        setSurveyDescription,
        questions,
        setQuestions,
        defaultQuestionType,
        addNewQuestion,
        handleDeleteQuestion,
        handleAddOption,
        handleTitleChange,
        handleQuestionTypeChange,
        handleOptionChange,
        handleSaveQuestion,
        handleEditQuestion,
        handleDuplicate,
        handleDeleteOption,
        onDragEnd,
        dupList,
        handleCreateSurvey,
      }}
    >
      {children}
    </CreateSurveyContext.Provider>
  );
};

// Hook to use in your components
export const useCreateSurveyProvider = () => useContext(CreateSurveyContext);
