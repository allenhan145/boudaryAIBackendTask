import React from "react";
import { DragDropContext, Droppable } from "@hello-pangea/dnd";
import { useCreateSurveyProvider } from "./CreateSurveyProvider";
import QuestionItem from "./QuestionItem";
import { motion } from "framer-motion";

const QuestionList = ({ questions }) => {
  const { onDragEnd } = useCreateSurveyProvider();

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId="questions" type="TASK" direction="vertical">
        {(provided) => (
          <div
            {...provided.droppableProps}
            ref={provided.innerRef}
            className="space-y-0.5"
          >
            {questions.map((question, index) => {
              if (!question) return null;
              return (
                <motion.div 
                  key={question.id}
                  initial={{ opacity: 0.8, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <QuestionItem
                    question={question}
                    index={index}
                  />
                </motion.div>
              );
            })}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
};

export default QuestionList;
