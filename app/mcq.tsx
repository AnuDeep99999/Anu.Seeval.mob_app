// app/mcq.tsx
import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  ScrollView,
  ActivityIndicator,
  Alert,
  Pressable,
  StyleSheet,
} from "react-native";
import API from "../src/lib/api";


type MCQ = {
  question: string;
  options: string[];
  answer: string; // must match one of options
};

export default function MCQGenerator() {
  const [course, setCourse] = useState("Python");
  const [topic, setTopic] = useState("Loops");
  const [subtopic, setSubtopic] = useState("For Loops");

  const [loading, setLoading] = useState(false);
  const [mcqs, setMcqs] = useState<MCQ[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>(
    {}
  );
  const [submitted, setSubmitted] = useState(false);

  const reset = () => {
    setSubmitted(false);
    setSelectedAnswers({});
    setCurrentQuestion(0);
    setMcqs([]);
  };

  const generateMCQs = async () => {
    setLoading(true);
    setSubmitted(false);
    setSelectedAnswers({});
    setCurrentQuestion(0);
    try {
      const res = await API.post("/topic-content/", {
        course,
        topic,
        subtopic,
      });

      // Expecting { content: MCQ[] }
      const content = res?.data?.content as MCQ[] | undefined;
      if (!Array.isArray(content) || content.length === 0) {
        Alert.alert("No questions", "Server returned no MCQs for your input.");
        setMcqs([]);
        return;
      }

      // Basic shape guard
      const valid = content.every(
        (q) =>
          typeof q?.question === "string" &&
          Array.isArray(q?.options) &&
          typeof q?.answer === "string"
      );
      if (!valid) {
        Alert.alert("Invalid response", "MCQ format from server is unexpected.");
        setMcqs([]);
        return;
      }

      setMcqs(content);
    } catch (error: any) {
      console.error(
        "MCQ Generation error:",
        error?.response?.data || error?.message || error
      );
      Alert.alert(
        "Error",
        error?.response?.data?.detail ||
          error?.message ||
          "Failed to generate MCQs."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (qIndex: number, option: string) => {
    if (submitted) return;
    setSelectedAnswers((prev) => ({ ...prev, [qIndex]: option }));
  };

  const handleSubmit = () => {
    if (mcqs.length === 0) return;
    if (Object.keys(selectedAnswers).length !== mcqs.length) {
      Alert.alert("Incomplete", "Please answer all questions before submitting.");
      return;
    }
    setSubmitted(true);
  };

  const calculateScore = () =>
    mcqs.reduce((acc, q, i) => (selectedAnswers[i] === q.answer ? acc + 1 : acc), 0);

  const renderQuestion = (q: MCQ, index: number) => (
    <View key={index} style={{ marginVertical: 10 }}>
      <Text style={{ fontWeight: "bold", marginBottom: 6 }}>
        {`Q${index + 1}: ${q.question}`}
      </Text>
      {q.options.map((opt, i) => {
        const isSelected = selectedAnswers[index] === opt;
        const isCorrect = submitted && opt === q.answer;
        const isWrong = submitted && isSelected && opt !== q.answer;

        return (
          <Pressable
            key={`${index}-${i}-${opt}`}
            onPress={() => handleOptionSelect(index, opt)}
            disabled={submitted}
            style={[
              styles.option,
              isSelected && !submitted && styles.optionSelected,
              submitted && isCorrect && styles.optionCorrect,
              submitted && isWrong && styles.optionWrong,
            ]}
            accessibilityRole="button"
            accessibilityState={{ selected: isSelected, disabled: submitted }}
          >
            <Text>{`${String.fromCharCode(97 + i)}) ${opt}`}</Text>
          </Pressable>
        );
      })}
    </View>
  );

  const renderSummary = () => (
    <View>
      <Text style={{ fontSize: 18, fontWeight: "bold", marginBottom: 10 }}>
        Your Score: {calculateScore()} / {mcqs.length}
      </Text>
      {mcqs.map((q, index) => {
        const selected = selectedAnswers[index];
        return (
          <View key={`summary-${index}`} style={{ marginVertical: 10 }}>
            <Text style={{ fontWeight: "bold" }}>{`Q${index + 1}: ${q.question}`}</Text>
            <Text>Your Answer: {selected || "Not Answered"}</Text>
            <Text style={{ color: selected === q.answer ? "green" : "red" }}>
              Correct Answer: {q.answer}
            </Text>
          </View>
        );
      })}
      <View style={{ marginTop: 16 }}>
        <Button title="Generate New Set" onPress={reset} />
      </View>
    </View>
  );

  return (
    <ScrollView contentContainerStyle={{ padding: 20 }}>
      {!mcqs.length && (
        <>
          <TextInput
            value={course}
            onChangeText={setCourse}
            placeholder="Course"
            style={styles.input}
          />
          <TextInput
            value={topic}
            onChangeText={setTopic}
            placeholder="Topic"
            style={styles.input}
          />
          <TextInput
            value={subtopic}
            onChangeText={setSubtopic}
            placeholder="Subtopic"
            style={styles.input}
          />
          <Button title="Generate MCQs" onPress={generateMCQs} />
        </>
      )}

      {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}

      {!submitted && mcqs.length > 0 && renderQuestion(mcqs[currentQuestion], currentQuestion)}

      {!submitted && mcqs.length > 0 && (
        <View
          style={{ flexDirection: "row", justifyContent: "space-between", marginTop: 20 }}
        >
          <Button
            title="Previous"
            disabled={currentQuestion === 0}
            onPress={() => setCurrentQuestion((q) => Math.max(0, q - 1))}
          />
          {currentQuestion < mcqs.length - 1 ? (
            <Button title="Next" onPress={() => setCurrentQuestion((q) => q + 1)} />
          ) : (
            <Button title="Submit" onPress={handleSubmit} />
          )}
        </View>
      )}

      {submitted && renderSummary()}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
  },
  option: {
    padding: 10,
    borderWidth: 1,
    borderRadius: 5,
    marginVertical: 4,
    backgroundColor: "#fff",
    borderColor: "#ccc",
  },
  optionSelected: { backgroundColor: "#bbdefb" },
  optionCorrect: { backgroundColor: "#c8e6c9", borderColor: "green" },
  optionWrong: { backgroundColor: "#ffcdd2", borderColor: "red" },
});
