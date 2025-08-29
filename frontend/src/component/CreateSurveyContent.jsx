import React from "react";
import { SixDotIcon } from "./Icons";
import { sidebarcontent } from "./helper";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { useCreateSurveyProvider } from "./CreateSurveyProvider";

const CreateSurveyContent = () => {
  const { questions, onDragEnd } = useCreateSurveyProvider();

  return (
    <div className="rounded-[20px] border-2 border-light-gray bg-white mt-3 flex flex-col  h-full sm:h-[calc(100vh-338px)] ">
      <div className="grow">
        <h3 className="auth-sub-heading text-primary font-medium border-b-2 border-light-gray p-3 w-full text-base ">
         Survey Questions
        </h3>
      </div>
      <div className="overflow-auto h-full scrollbar-style min-h-[84px] max-h-[200px]  sm:max-h-full">
        <div className="flex flex-col px-4 pb-4 ">
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="droppableId">
              {(provided, snapshot) => (
                <div
                  style={{
                    backgroundColor: snapshot.isDragging
                      ? "lightblue"
                      : "white",
                  }}
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                >
                  {questions.map((list, index) => (
                    <Draggable
                      key={index}
                      draggableId={index.toString()}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          key={index}
                          className="flex justify-between items-center border-b border-lightlavender py-3 "
                        >
                          <p className="text-sm font-switzer text-primary whitespace-nowrap text-ellipsis overflow-hidden max-w-[240px]">
                            {list.title}
                          </p>
                          <span>
                            <SixDotIcon />
                          </span>
                        </div>
                      )}
                    </Draggable>
                  ))}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
      </div>
    </div>
  );
};

export default CreateSurveyContent;
