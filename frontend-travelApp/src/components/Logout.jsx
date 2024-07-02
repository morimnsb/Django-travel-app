import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Remove the 'jwt' cookie
    // Remove 'csrftoken' cookie
    Cookies.remove('isLoggedIn', { domain: 'localhost', path: '/' });

    // Optionally, you can remove other local storage items as well
    localStorage.removeItem('token');
    localStorage.removeItem('Userinfo');
    localStorage.removeItem('user');
    localStorage.removeItem('avatar');

    // Redirect to the home page
    navigate('/');
  }, [navigate]); // Empty dependency array to ensure useEffect runs only once on mount

  return null; // You can return null or any other component, as the main purpose is the side effect
};

export default Logout;
