import React, { useState } from 'react'

export default function AdminDelete({onDataFromChild}) {
  
    const sendDataToParent = () => {    
        onDataFromChild(false); 
      };
  return (
    <>
    <div className='w-140 h-80 mt-36 ml-24 bg-sidebar border border-gray-600 z-10 absolute'>
            <div className='flex p-3 pr-1'>
                <i class='bx bx-user-x text-4xl mr-3 mt-2' ></i>
                <p className='text-xl font-bold text-background mt-3'>DELETE CONFIRMATION</p>
                <i onClick={sendDataToParent} className='bx bx-x text-5xl font-light ml-auto text-red-500 cursor-pointer'></i>
            </div>

            <div className='flex justify-center items-center text-lg text-background font-semibold mt-16'>
                <p>ARE YOU SURE YOU WANT TO DELETE CHRIS WONG? </p>
            </div>

            <div className='flex justify-end mt-24 mr-6 '>
            <button className="bg-transparent font-bold text-red-700 border border-background px-8 py-2">
                DELETE
            </button>
            </div>
           
    </div>
    </>
  )
}
