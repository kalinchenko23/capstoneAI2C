import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface FAQProps {
  question: string;
  answer: string;
  value: string;
}

const FAQList: FAQProps[] = [
  {
    question: "Do I need to have my own Google API key?",
    answer: "Yes. It is nessesarry for each user to have their own keys.",
    value: "item-1",
  },
  {
    question: "Do I have to use LLM/VLM capabilities?",
    answer:
      "No, LLM/VLM capabilities are optional.",
    value: "item-2",
  },
  {
    question:
      "What are the estimated charges telling me?",
    answer:
      "The estimated charges are a ROUGH estimate of time that the query will take and cost that will be billed to your GoogleAPI/OpenAI account?",
    value: "item-3",
  },
  {
    question: "What do I do if my API keys are no longer working?",
    answer: "Unfortunateley, right now maintaining the API keys is an individual responsibility of each user.",
    value: "item-4",
  },
  {
    question:
      "Are my queries beibg stored for a later review?",
    answer:
      "No, there are no query history.",
    value: "item-5",
  },
];

export const FAQ = () => {
  return (
    <section
      id="faq"
      className="container py-24 sm:py-32  text-gray-300  shadow-md"
    >
      <h2 className="text-3xl md:text-4xl font-bold mb-6 text-center">
        Frequently Asked{" "}
        <span className="text-yellow-500">Questions</span>
      </h2>

      <Accordion
        type="single"
        collapsible
        className="w-full AccordionRoot"
      >
        {FAQList.map(({ question, answer, value }: FAQProps) => (
          <AccordionItem
            key={value}
            value={value}
            className="border-b border-yellow-500"
          >
            <AccordionTrigger className="text-left text-lg font-semibold hover:text-yellow-600 transition-colors">
              {question}
            </AccordionTrigger>

            <AccordionContent className="text-gray-300  rounded-lg p-4 mt-1">
              {answer}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>

      <h3 className="font-medium mt-10 text-center">
        Still have questions?{" "}
        <a
          rel="noreferrer noopener"
          href="#"
          className="text-yellow-500 transition-all border-yellow-600 hover:border-b-2"
        >
          Contact us
        </a>
      </h3>
    </section>
  );
};
