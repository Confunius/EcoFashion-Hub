import React, { useState } from "react";
import girl from "../assets/girl.jpg";
export default function CutomerUpdate({ onDataFromChild }) {
  const sendDataToParent = () => {
    onDataFromChild(false);
  };
  return (
    <>
      <div className="w-140 h-96 mt-28 ml-24 bg-sidebar border border-gray-600 z-10 absolute">
        <div className="flex items-center ml-5 mt-3 mr-3">
          <i class="bx bxs-user-circle text-4xl mt-3 ml-3"></i>
          <p className="text-lg font-bold mt-2 ml-2 text-background">
            EDIT ACCOUNT
          </p>
          <i
            onClick={sendDataToParent}
            className="bx bx-x text-5xl font-light ml-auto text-red-500 cursor-pointer"
          ></i>
        </div>

        <div className="flex mt-4">
          <div className="ml-10">
            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-md ">
                First Name:{" "}
              </p>
              <input
                className="border border-black p-1 w-8/12 bg-transparent"
                type="text"
                name=""
                id=""
                placeholder="First Name"
              />
            </div>
            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-md ">
                Email:{" "}
              </p>
              <input
                className="border border-black p-1 w-8/12 bg-transparent"
                type="text"
                name=""
                id=""
                placeholder="Email"
              />
            </div>
            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-md ">
                Address:{" "}
              </p>
              <input
                className="border border-black p-1 w-80 bg-transparent"
                type="text"
                name=""
                id=""
                placeholder="Address"
              />
            </div>
          </div>

          <div className="ml-10">
            <div>
              <p className="text-background font-semibold mb-1 text-md">
                Gender:{" "}
              </p>
              <div className="mt-3 flex justify-center mb-2">
                <input type="radio" name="gender" className="h-5 w-5 cursor-pointer" />{" "}
                <span className="text-background font-semibold ml-2  text-md">
                  {" "}
                  Male
                </span>
                <input type="radio" name="gender" className="h-5 w-5 cursor-pointer ml-10" />
                <span className="text-background font-semibold ml-2 text-md">
                  Female
                </span>
              </div>
            </div>

            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-md ">
                Postal Code:{" "}
              </p>
              <input
                className="border border-black p-1 w-full bg-transparent"
                type="text"
                name=""
                id=""
                placeholder="Postal Code"
              />
            </div>

            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-md ">
                Birthday:{" "}
              </p>
              <input
                className="border border-black p-1 w-full bg-transparent"
                type="text"
                name=""
                id=""
                placeholder="Birth Date"
              />
            </div>
          </div>
        </div>

        <div className="flex ml-12 m-2">
          <div>
            <p className="text-background font-medium ">Account Updated By: </p>
            <p className="text-lg font-semibold">ChrisW </p>
            <p className="text-background font-medium">Last Updated 03/05/2020 </p>
          </div>

          <div className="ml-auto mt-7 mr-7">
            <button className="bg-transparent font-semibold text-background border border-background px-8 py-2">
              DONE
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
