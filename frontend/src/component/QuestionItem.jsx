import React from "react";
import { Draggable } from "@hello-pangea/dnd";
import { Tooltip } from "react-tooltip";
import { FaStar } from "react-icons/fa";
import { CopyIcon2, DeleteIcon, EditIcon } from "./Icons";
import { DraggableIcon } from "./CommonIcons";
import { EmptyStarIcon, FilledStarIcon, SelectArrowIcon } from "./Icons.jsx";
import { useCreateSurveyProvider } from "./CreateSurveyProvider";
import RenderCheckboxOptions from "./RenderCheckboxOptions";
import RenderMultipleOptions from "./RenderMultipleOptions";
import { motion, AnimatePresence } from "framer-motion";


const QuestionItem = ({ question, index }) => {
  const {
    handleDeleteOption,
    handleAddOption,
    handleTitleChange,
    handleQuestionTypeChange,
    handleOptionChange,
    handleDeleteQuestion,
    handleSaveQuestion,
    handleEditQuestion,
    handleDuplicate,
    dupList,
  } = useCreateSurveyProvider();


  const renderOptions = (q, questionIndex) => {
    switch (q.type) {
      case "multipleChoice":
        return (q.options || []).map((option, optionIndex) => (
          <RenderCheckboxOptions
            key={option.id}
            questionIndex={questionIndex}
            question={q}
            option={option}
            optionIndex={optionIndex}
            dupList={dupList}
          />
        ));
      case "singleChoice":
        return (q.options || []).map((option, optionIndex) => (
          <RenderMultipleOptions
            key={option.id}
            questionIndex={questionIndex}
            question={q}
            option={option}
            optionIndex={optionIndex}
            dupList={dupList}
          />
        ));
      case "openQuestion":
        return (
          <div className="w-full my-2 border border-gray-200 rounded-lg bg-[#f9f9fc]">
            <textarea
              className="w-full h-24 p-3 bg-transparent border-none outline-none resize-none text-gray-600 placeholder-gray-400"
              disabled={true}
              placeholder="Enter your long answer here..."
              onChange={(e) => handleOptionChange(questionIndex, 0, e.target.value)}
            />
          </div>
        );
      case "shortAnswer":
        return (
          <div className="w-full my-2 border border-gray-200 rounded-lg bg-[#f9f9fc]">
            <input
              className="w-full p-2 bg-transparent border-none outline-none text-gray-600 placeholder-gray-400"
              disabled={true}
              placeholder="Enter your short answer here..."
              onChange={(e) => handleOptionChange(questionIndex, 0, e.target.value)}
            />
          </div>
        );
      case "scale":
      case "npsScore":
        return (
          <div className="w-full my-4 bg-white rounded-lg">
            <div className="flex flex-col items-center justify-center py-4">
              <div className="flex items-center justify-center gap-2 flex-wrap">
                {[...Array(10)].map((_, idx) => (
                  <div
                    key={idx}
                    className="cursor-pointer group relative"
                  >
                    {/* Empty star (background) */}
                    <EmptyStarIcon />

                    {/* Filled star (overlay on hover) */}
                    <FilledStarIcon />
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      // case "npsScore":
      //   return (
      //     <div className="w-full my-6 bg-white rounded-lg">
      //       <div className="flex flex-col items-center justify-center py-6 px-4">
      //         {/* Gradient bar background */}
      //         <div className="relative w-full max-w-3xl mb-4 mt-2">
      //           <div className="h-2 rounded-full w-full bg-gradient-to-r from-red-400 via-yellow-300 to-green-500"></div>
      //         </div>
      //
      //         {/* Number indicators */}
      //         <div className="flex items-center justify-between w-full max-w-3xl px-2">
      //           {[...Array(11)].map((_, idx) => (
      //             <div key={idx} className="flex flex-col items-center group cursor-pointer">
      //               <div
      //                 className={`w-10 h-10 mb-1.5 flex items-center justify-center rounded-full transition-all duration-200
      //                   ${idx === 0 ? 'bg-red-400 hover:bg-red-500' :
      //                     idx < 4 ? 'bg-orange-400 hover:bg-orange-500' :
      //                     idx < 7 ? 'bg-yellow-400 hover:bg-yellow-500' :
      //                     idx < 9 ? 'bg-lime-400 hover:bg-lime-500' :
      //                     'bg-green-500 hover:bg-green-600'}
      //                   shadow-sm hover:shadow group-hover:scale-110`}
      //               >
      //                 <span className="text-white font-medium">{idx}</span>
      //               </div>
      //
      //               {/* Indicator label */}
      //               <span className="text-xs text-gray-500">
      //                 {idx === 0 ? 'Not likely' :
      //                  idx === 5 ? 'Neutral' :
      //                  idx === 10 ? 'Very likely' : ''}
      //               </span>
      //             </div>
      //           ))}
      //         </div>
      //
      //         {/* Legend */}
      //         <div className="flex justify-between w-full max-w-3xl mt-8 px-4">
      //           <div className="text-center">
      //             <span className="text-sm text-gray-600 font-medium">Detractors</span>
      //             <div className="h-1 w-16 bg-red-400 mx-auto mt-1"></div>
      //           </div>
      //           <div className="text-center">
      //             <span className="text-sm text-gray-600 font-medium">Passives</span>
      //             <div className="h-1 w-16 bg-yellow-400 mx-auto mt-1"></div>
      //           </div>
      //           <div className="text-center">
      //             <span className="text-sm text-gray-600 font-medium">Promoters</span>
      //             <div className="h-1 w-16 bg-green-500 mx-auto mt-1"></div>
      //           </div>
      //         </div>
      //       </div>
      //     </div>
      //   );
      default:
        return null;
    }
  };

  return (
    <Draggable draggableId={question.id.toString()} index={index}>
      {(provided) => (
        <div
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          ref={provided.innerRef}
          className={`flex font-switzer rounded-[12px] mb-4 flex-col p-4 border-2 transition-all duration-200 shadow-sm hover:shadow-md ${
            question.isTag
              ? "border-[#4d3b7c] bg-[#f7f5fb]"
              : question.saved
              ? "border-[#6851a7] bg-white"
              : "border-[#6851a7] bg-white"
          }`}
        >
          {question.isTag && (
            <div
              className="flex items-center gap-2 mb-2 px-2 py-1 bg-[#f7f5fb] w-fit rounded-full"
            >
              <FaStar className="text-[#6851a7] text-xs"/>
              <span className="text-xs text-gray-700 font-medium">
                Tag: {question.title}
              </span>
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSaveQuestion(index);
            }}
          >
            <div className="flex justify-center mb-2 cursor-move">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                <DraggableIcon className="text-gray-400 opacity-50" />
              </motion.div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 mb-3">


            {question.saved || question.isTag ? (
              <p className="px-2 py-1.5 text-gray-800 font-normal text-base sm:col-span-8 bg-transparent border border-gray-200 rounded-lg">
                {question.title || "Enter your question"}
              </p>
              ) : (
              <motion.input
                whileFocus={{ boxShadow: "0 0 0 2px rgba(104, 81, 167, 0.15)" }}
                type="text"
                required
                value={question.title}
                placeholder="Enter your question here..."
                onChange={(e) => handleTitleChange(index, e.target.value)}
                className="px-2 py-1.5 text-gray-800 outline-none font-normal text-base sm:col-span-8 bg-transparent border border-gray-200 rounded-lg focus:ring-1 focus:ring-[#6851a7] focus:border-transparent transition-all duration-200"
              />
            )}

              {!question.saved && !question.isTag ? (
                <div className="relative sm:col-span-4">
                  <motion.select
                    whileHover={{ boxShadow: "0 0 0 1px rgba(104, 81, 167, 0.1)" }}
                    value={question.type}
                    onChange={(e) => handleQuestionTypeChange(index, e.target.value)}
                    className="cursor-pointer text-sm px-2 py-1.5 border border-[#6851a7] rounded-lg bg-white appearance-none focus:outline-none focus:ring-1 focus:ring-[#6851a7] focus:border-transparent transition-all duration-200 text-gray-700 w-full pr-8"
                  >
                    <option value="singleChoice">
                      Single Choice
                    </option>
                    <option value="multipleChoice">
                      Multiple Choice
                    </option>
                    <option value="openQuestion">
                      Long Answer
                    </option>
                    <option value="shortAnswer">
                      Short Answer
                    </option>
                    <option value="scale">Ratings</option>
                    <option value="npsScore">NPS Score</option>
                  </motion.select>
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
                    <SelectArrowIcon width={14} height={14} />
                  </div>
                </div>
              ) : (
                question.isTag ? (
                  <div className="flex items-center justify-end sm:col-span-4">
                    <motion.span
                      whileHover={{ scale: 1.02 }}
                      className="px-2 py-1.5 bg-[#e8e3f4] text-[#6851a7] rounded-lg text-xs font-medium w-full text-center"
                    >
                      {question.type === "singleChoice" ? "Single Choice Question" : "Multiple Choice Question"}
                    </motion.span>
                  </div>
                ) : (
                  <div className="flex items-center justify-end sm:col-span-4">
                    <motion.span
                      whileHover={{ scale: 1.02 }}
                      className="px-2 py-1.5 bg-[#f4f2fb] text-[#6851a7] rounded-lg text-xs font-medium w-full text-center"
                    >
                      {question.type === "singleChoice" ? "Single Choice" :
                       question.type === "multipleChoice" ? "Multiple Choice" :
                       question.type === "openQuestion" ? "Long Answer" :
                       question.type === "shortAnswer" ? "Short Answer" :
                       question.type === "scale" ? "Rating Scale" : 
                       question.type === "npsScore" ? "NPS Score" : "Unknown"}
                    </motion.span>
                  </div>
                )
              )}
            </div>

            <div className="mb-2">
              {["multipleChoice", "singleChoice"].includes(question.type) && (
                <div className="space-y-2">
                  {renderOptions(question, index)}
                  {!question.saved && (
                    <button
                      disabled={question.saved}
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleAddOption(index);
                      }}
                      className={`mt-5 disabled:opacity-70 bg-[#6851a7] hover:bg-[#5b4691] text-white py-2 px-4 rounded-full font-medium transition-all duration-200`}
                    >
                      Add Option (Q{index})
                    </button>
                  )}
                </div>
              )}

              {["openQuestion", "shortAnswer", "scale", "npsScore"].includes(
                question.type
              ) && <div>{renderOptions(question, index)}</div>}
            </div>

            <div className="flex justify-end items-center gap-2">
              {!question.saved && (
                <>
                  {!question.isTag && (
                    <>
                      <Tooltip id="delete-btn" />
                      <motion.button
                        whileHover={{ scale: 1.05, backgroundColor: "rgba(239, 68, 68, 0.1)" }}
                        whileTap={{ scale: 0.97 }}
                        data-tooltip-id="delete-btn"
                        data-tooltip-content="Delete Question"
                        data-tooltip-place="top"
                        onClick={() => handleDeleteQuestion(index)}
                        type="button"
                        className="p-2 rounded-full hover:bg-red-50 transition-all duration-200"
                      >
                        <DeleteIcon className="text-red-500 w-4 h-4" />
                      </motion.button>

                      <Tooltip id="copy-btn" />
                      <motion.button
                        whileHover={{ scale: 1.05, backgroundColor: "rgba(104, 81, 167, 0.1)" }}
                        whileTap={{ scale: 0.97 }}
                        data-tooltip-id="copy-btn"
                        data-tooltip-content="Duplicate Question"
                        data-tooltip-place="top"
                        type="button"
                        onClick={() => handleDuplicate(index)}
                        className="p-2 rounded-full hover:bg-purple-50 transition-all duration-200"
                      >
                        <CopyIcon2 className="text-[#6851a7] w-4 h-4" />
                      </motion.button>
                    </>
                  )}

                  {/* Save button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    className={`px-5 py-2 text-white font-medium rounded-full shadow-sm transition-all duration-200 ${
                      question.isTag
                        ? "bg-[#6851a7] hover:bg-[#5b4691]"
                        : "bg-[#6851a7] hover:bg-[#5b4691]"
                    }`}
                  >
                    Save Question
                  </motion.button>
                </>
              )}

              {question.saved && (
                <>
                  <Tooltip id="delete-saved-btn" />
                  <motion.button
                    whileHover={{ scale: 1.05, backgroundColor: "rgba(239, 68, 68, 0.1)" }}
                    whileTap={{ scale: 0.97 }}
                    data-tooltip-id="delete-saved-btn"
                    data-tooltip-content="Delete Question"
                    data-tooltip-place="top"
                    onClick={() => handleDeleteQuestion(index)}
                    type="button"
                    className="p-2 rounded-full hover:bg-red-50 transition-all duration-200"
                  >
                    <DeleteIcon className="text-red-500 w-4 h-4" />
                  </motion.button>

                  <Tooltip id="edit-btn" />
                  <motion.button
                    whileHover={{ scale: 1.05, backgroundColor: "rgba(104, 81, 167, 0.1)" }}
                    whileTap={{ scale: 0.97 }}
                    data-tooltip-id="edit-btn"
                    data-tooltip-content="Edit Question"
                    data-tooltip-place="top"
                    onClick={() => handleEditQuestion(index)}
                    className="p-2 rounded-full hover:bg-purple-50 transition-all duration-200"
                  >
                    <EditIcon className="text-[#6851a7] w-4 h-4" />
                  </motion.button>
                </>
              )}
            </div>
          </form>
        </div>
      )}
    </Draggable>
  );
};

export default QuestionItem;
