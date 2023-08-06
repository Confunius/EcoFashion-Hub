import React, { useState } from 'react'
import girl from '../assets/girl.jpg'
export default function CutomerInfo({onDataFromChild}) {
    const [isOpenModal,setIsOpenModal] = useState(false)
    const [isBan,setIsBan] = useState(false)
    const [isSuspend,setIsSuspend] = useState(false)

    

    const sendDataToParent = () => {    
        onDataFromChild(false); 
      };
  return (
    <>
    <div className='w-140 h-80 mt-36 ml-24 bg-sidebar border border-gray-600 z-10 absolute'>
            <div className='flex'>
                <p className='text-lg font-bold p-2 text-background'>MORE DETAILS</p>
                <i onClick={sendDataToParent} className='bx bx-x text-5xl font-light ml-auto text-red-500 cursor-pointer'></i>
            </div>
            <div className='flex px-3'>
                <div className='flex flex-col items-center'>
                     <img src={girl} alt="pic" className='h-48 w-48' />
                     <p className='mt-1 font-semibold'>Krystal Tan</p>
                </div>

                <div className='ml-10 font-medium'>
                    <p className='mb-3'>Email:</p>
                    <p className='mb-3'>Gender:</p>
                    <p className='mb-3'>Address:</p>
                    <p className='mb-3'>Postal Code:</p>
                    <p className='mb-3'>Birth date:</p>
                    {isBan || isSuspend && <p className=''>Status:</p>}
                    
                </div>

                <div className='ml-10 font-semibold'>
                    <p className='mb-3'>krystal123@gmail.com</p>
                    <p className='mb-3'>Female</p>
                    <p className='mb-3'>Seletar Road Block 123A</p>
                    <p className='mb-3'>301103</p>
                    <p className='mb-3'>29/04/2003</p>
                    {isBan && <p className='text-red-500 font-bold'>BANNED</p>}
                    {isBan ? '': isSuspend ? <p>Suspend for 150 days</p>:''}
                </div>
            </div>
            {!isBan ? 
           <div className='flex justify-end mr-4 mb-6'>
           <button
                 onClick={()=>{setIsBan(true)}}
                 className="border border-black mr-4 w-28 h-10 font-semibold text-red-700 hover:bg-red-200"
               >
                 BAN
           </button>

           <button
                 onClick={()=> isSuspend?setIsSuspend(false):setIsSuspend(true)}
                 className="border border-black w-28 h-10 font-semibold text-black hover:bg-gray-200"
               >
                 {isSuspend ? 'UN-SUSPEND': 'SUSPEND'}
           </button>

           </div> : <p className='text-red-500 font-semibold text-lg ml-16 mt-4'>User has been banned. (Failure to comply our guidlines)</p>  
          }
           
    </div>
    </>
  )
}
