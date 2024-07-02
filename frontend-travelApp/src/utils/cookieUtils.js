// cookieUtils.js
import Cookies from 'js-cookie';

export const isAccessTokenSet = () => {
  const accessToken = Cookies.get('access_token '); // Replace with your actual cookie name
  return !!accessToken;
};