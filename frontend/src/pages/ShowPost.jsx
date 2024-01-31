import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router";
import BackButton from "../components/BackButton";
import PostDetails from "../components/PostDetails";
import { IoIosArrowRoundBack } from "react-icons/io";
import { useNavigate } from "react-router-dom";
import { getStorage, ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';
import { app } from '../config/firebase.config';
import { isImageValid } from "../utils/imageFormatUtils"; // Import the function

const ShowPost = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [post, setPost] = useState({});
  const [isEditMode, setIsEditMode] = useState(false);
  const [newImages, setNewImages] = useState(null);
  const [formatError, setFormatError] = useState(null);

  useEffect(() => {
    const fetchPostDetails = async () => {
      try {
        const response = await axios.get(`/posts/details/${id}`);
        setPost(response.data);
      } catch (error) {
        console.error("Error fetching post details:", error);
      }
    };

    fetchPostDetails();
  }, [id]);

  const handleEditMode = () => {
    setIsEditMode(!isEditMode);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPost((prevPost) => ({ ...prevPost, [name]: value }));
  };

  const handleSave = async () => {
    try {
      const response = await axios.put(`/posts/update/${id}`, post);
      setIsEditMode(false);
      console.log(response);
    } catch (error) {
      console.error("Error updating post:", error);
    }
  };

  const handleImageUpload = async (files) => {
    try {
      const storage = getStorage(app);
      const imagePaths = [];

      for (let i = 0; i < files.length; i++) {
        const fileName = new Date().getTime() + files[i].name;
        const storageRef = ref(storage, "images/" + fileName);
        await uploadBytesResumable(storageRef, files[i], {
          contentType: files[i].type,
        });

        // Get the public URL of the uploaded file
        const publicUrl = await getDownloadURL(storageRef);
        console.log("File available at", publicUrl);
        imagePaths.push(publicUrl);
      }

      const formData = new FormData();

      for (let i = 0; i < files.length; i++) {
        formData.append("images", files[i]);
      }
      // Check if the image format is valid
      if (!isImageValid(files)) {
        setFormatError(
          "Some of the selected files are not in a supported format. Please only upload files in JPEG or PNG format."
        );
        // Clear error after 3 seconds
        setTimeout(() => {
          setFormatError(null);
        }, 3000);

        return;
      }

      const response = await axios.put(`/posts/update/${id}`, formData, {
        images: imagePaths,
      });
      console.log(response.data.post);
      setPost(response.data.post);
    } catch (error) {
      console.error("Error updating post with new image:", error);
    }
  };

  const handleImageDelete = async (index) => {
    try {
      const filename = post.images[index].slice(-24);
      await axios.delete(`/posts/images/delete/${post._id}/${filename}`);
      setPost((prevPost) => ({
        ...prevPost,
        images: prevPost.images.filter((_, i) => i !== index),
      }));
    } catch (error) {
      console.error("Error deleting image:", error);
    }
  };

  return (
    <div className="mx-auto p-10 mt-16 overflow-hidden dark:bg-gray-950 min-h-screen">
      <BackButton />
      {JSON.parse(localStorage.getItem("Userinfo")).username === post.writer ? (
        <>
          <PostDetails
            post={post}
            isEditMode={isEditMode}
            handleSave={handleSave}
            handleInputChange={handleInputChange}
            handleImageUpload={handleImageUpload}
            handleImageDelete={handleImageDelete}
            handleEditMode={handleEditMode}
          />
          {/* Add new image */}
          <div className="mb-4 ml-7 dark:text-slate-200 dark:bg-gray-950">
            <label
              htmlFor="newImages"
              className="dark:text-slate-300 block mt-5 text-2xl"
            >
              Add new image(s) to the current post
            </label>
            <input
              type="file"
              name="images"
              multiple
              accept="image/*"
              onChange={(e) => setNewImages(e.target.files)}
              className="border-2 p-3 mt-2"
            />
            <button
              onClick={() => handleImageUpload(newImages)}
              className="bg-gray-800 text-white p-4 px-6 mt-2 dark:bg-slate-300 dark:text-gray-900"
            >
              Upload
            </button>
            {formatError && (
              <p className="text-red-600 mt-2 font-semibold">{formatError}</p>
            )}
          </div>
          <button
            onClick={() => navigate(-1)}
            className="text-lg flex items-center gap-1 ml-7 text-teal-600"
          >
            <IoIosArrowRoundBack /> Back
          </button>
        </>
      ) : (
        <>
          <h3 className="text-teal-600 text-3xl mt-4 dark:text-white">
            {post.title}
          </h3>
          <p className="text-slate-800 font-semibold mt-2 dark:text-slate-200">
            {post.place}
          </p>
          <p className="text-slate-900 mt-4 leading-snug dark:text-slate-200">
            {post.description}
          </p>

          <button
            onClick={() => navigate(-1)}
            className="text-lg flex items-center gap-1 text-teal-600"
          >
            <IoIosArrowRoundBack /> Back
          </button>
        </>
      )}
    </div>
  );
};

export default ShowPost;
