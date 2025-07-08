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
    question: "Is this template free?",
    answer: "Yes. It is a free ChadcnUI template.",
    value: "item-1",
  },
  {
    question: "Lorem ipsum dolor sit amet consectetur adipisicing elit?",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Sint labore quidem quam? Consectetur sapiente iste rerum reiciendis animi nihil nostrum sit quo, modi quod.",
    value: "item-2",
  },
  {
    question:
      "Lorem ipsum dolor sit amet  Consectetur natus dolores minus quibusdam?",
    answer:
      "Lorem ipsum dolor sit amet consectetur, adipisicing elit. Labore qui nostrum reiciendis veritatis necessitatibus maxime quis ipsa vitae cumque quo?",
    value: "item-3",
  },
  {
    question: "Lorem ipsum dolor sit amet, consectetur adipisicing elit?",
    answer: "Lorem ipsum dolor sit amet consectetur, adipisicing elit.",
    value: "item-4",
  },
  {
    question:
      "Lorem ipsum dolor sit amet consectetur adipisicing elit. Consectetur natus?",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Sint labore quidem quam? Consectetur sapiente iste rerum reiciendis animi nihil nostrum sit quo, modi quod.",
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
