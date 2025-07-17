import { FAQ } from "./components/FAQ";
import { Instructions }  from "./components/Instructions";
import MapWithFormBelow from "./components/Map"
import { Navbar } from "./components/Navbar";
import "./App.css";

function App() {
  
  return (
    <>
      <Navbar />
      <Instructions />
      <MapWithFormBelow />
      <FAQ />
    </>
  );
}

export default App;
