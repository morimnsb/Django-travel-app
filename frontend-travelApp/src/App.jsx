import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { isAccessTokenSet } from './utils/cookieUtils.js'; // Adjust the path accordingly

import axios from 'axios';
//Components & pages
import Home from './pages/Home';
import CreatePost from './pages/CreatePost';
import ShowPost from './pages/ShowPost';
import DeletePost from './pages/DeletePost';
import Navbar from './components/Navbar';
import Logout from './components/Logout';
import SignUp from './pages/SignUp';
import SignIn from './pages/SignIn';
import PostList from './components/PostList';
import NotFound from './pages/NotFound';
import Footer from './components/Footer';
import UserPanel from './pages/UserPanel';
import LocationsPage from './pages/LocationsPage';
import ScrollToTop from './components/ScrollToTop';
// Provider context
import { ThemeProvider } from './context/ThemeContext';
import { AvatarProvider } from './components/AvatarContext.jsx';

// Toastify
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Cookies from 'js-cookie';

// Default axios
// axios.defaults.baseURL = "https://ontheroad-travel-app.vercel.app";
axios.defaults.withCredentials = true;

function App() {
  const [themeMode, setThemeMode] = useState('light');
  const [isLoggedIn, setIsLoggedIn] = useState(isAccessTokenSet());

  const darkTheme = () => {
    setThemeMode('dark');
  };

  const lightTheme = () => {
    setThemeMode('light');
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      const loggedIn = isAccessTokenSet();
      setIsLoggedIn(loggedIn);
    }, 10000); // Check every 10 seconds
    console.log(isLoggedIn);
    
    return () => clearInterval(intervalId); // Cleanup on unmount or re-render
  }, [isLoggedIn]);

  return (
    <ThemeProvider value={{ themeMode, darkTheme, lightTheme }}>
      <AvatarProvider>
        <BrowserRouter>
          <ToastContainer />
          <Navbar />
          <ScrollToTop />
          <Routes>
            {isLoggedIn ? (
              <>
                <Route exact path="/" element={<PostList />} />
                <Route exact path="/posts/create" element={<CreatePost />} />
                <Route exact path="/posts/details/:id" element={<ShowPost />} />
                <Route
                  exact
                  path="/posts/delete/:id"
                  element={<DeletePost />}
                />
                <Route exact path="/locations" element={<LocationsPage />} />
                <Route exact path="/logout" element={<Logout />} />
                <Route path="/userPanel/:username" element={<UserPanel />} />
              </>
            ) : (
              <>
                <Route exact path="/" element={<SignIn />} />
                <Route exact path="/signin" element={<SignIn />} />
                <Route exact path="/signUp" element={<SignUp />} />
              </>
            )}
            <Route exact path="/*" element={<NotFound />} />
          </Routes>
          <Footer />
        </BrowserRouter>
      </AvatarProvider>
    </ThemeProvider>
  );
}

export default App;
