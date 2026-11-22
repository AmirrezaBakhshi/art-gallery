import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Home from "./Components/Pages/Home";
import Login from "./Components/Pages/Login";
import Signup from "./Components/Pages/Signup";
import Dashboard from "./Components/Pages/Dashboard";
import AddItem from "./Components/Pages/AddItem";
import AdditionalInfo from "./Components/Pages/AdditionalInfo";
import Library from "./Components/Pages/Library";
import EditInfo from "./Components/Pages/EditInfo";
import MuseumInfo from "./Components/Pages/MuseumInfo";
import ItemInfo from "./Components/Pages/ItemInfo";
import LibraryItemInfo from "./Components/Pages/LibraryItemInfo";
import EditItem from "./Components/Pages/EditItem";
import ProtectedRoute from "./Components/ProtectedRoute";
import AboutUs from "./Components/Pages/AboutUs";
import HowToUse from "./Components/Pages/HowToUse";
import './locale.jsx';

function App() {

  return (
    <>
    
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/aboutus" element={<AboutUs />} />
        <Route path="/how-to-use" element={<HowToUse />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/additem" element={<ProtectedRoute><AddItem /></ProtectedRoute>} />
        <Route path="/editinfo" element={<ProtectedRoute><EditInfo /></ProtectedRoute>} />
        <Route path="/library" element={<ProtectedRoute><Library /></ProtectedRoute>} />
        <Route path="/libraryiteminfo/:index" element={<LibraryItemInfo />} />
        <Route path="/editItem" element={<ProtectedRoute><EditItem /></ProtectedRoute>} />
        <Route path="/iteminfo/:index" element={<ItemInfo />} />
        <Route path="/museuminfo" element={<MuseumInfo />} />
        <Route path="/additionalinfo" element={<ProtectedRoute><AdditionalInfo /></ProtectedRoute>} />
        <Route path="*" element={<Home />} />
      </Routes>
    </BrowserRouter>
    
    </>
    
  );
}

export default App;
