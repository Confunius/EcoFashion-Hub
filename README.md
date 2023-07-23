# EcoFashion - Transforming Fashion with *Sustainability* and **Innovation**

> Welcome to EcoFashion, where fashion meets sustainability in perfect harmony! Our team of dedicated experts is committed to providing you with an exceptional shopping experience while making a positive impact on the environment.

## Meet Our Team

Responsibilities | *Wei Heng* | *Ethan* | *Ching Yi*
--- | --- | --- | ---
Product Page | ✔️ | | 
Product Information | ✔️ | | 
Shopping Cart | ✔️ | | 
Order Tracking | ✔️ | | 
Refund | ✔️ | | 
Order Management | ✔️ | | 
Product Management | ✔️ | | 
Promo Code Management | ✔️ | | 
Review Management | ✔️ | | 
README.md | ✔️ | | 
base.html | ✔️ | | 
Sustainability Page | ✔️ | | 
Customer Service | | ✔️ | 
Resolving Tickets | | ✔️ | 
FAQ | | ✔️ | 
Chat | | ✔️ | 
Homepage | | | ✔️
Login & Sign Up | | | ✔️
Account Information & Password | | | ✔️
Wishlist | | | ✔️
Order Status & History | | | ✔️
Account Deletion | | | ✔️
Payment Methods | | | ✔️

> *Note: ✔️ represents the responsibilities handled by each team member.*

## Wei Heng - The Product Maestro

> **Wei Heng** is our product expert, ensuring that each item in our collection embodies the essence of sustainability. From the captivating *Product Page* to the detailed *Product Information*, **Wei Heng's** expertise shines through.

## Ethan - The Customer Whisperer

> **Ethan** is the heart and soul of our *Customer Service*. With a passion for people and a drive to deliver excellence, **Ethan** is your go-to ally for *resolving inquiries*, *managing Tickets*, and providing answers in our comprehensive *FAQ* section.

## Ching Yi - The Interface Virtuoso

> **Ching Yi** is the mastermind behind our user-friendly interface. From the captivating *Homepage* to seamless *Account Information and Password* management, **Ching Yi's** artistry makes navigation a breeze.

# Running EcoFashion Hub Website Locally

In this guide, we will walk you through the steps to run the EcoFashion Hub website on your local device. The website is hosted on GitHub, and you can run it using CodeSpaces or other methods.

<details>
  <summary>Prerequisites</summary>
Before you begin, ensure that you have the following installed on your device:

1. Python: Make sure you have Python installed. You can download the latest version from the official Python website (https://www.python.org/downloads/).

2. Git: Install Git on your machine if you haven't already. You can download it from the official Git website (https://git-scm.com/downloads).

## Cloning the Repository

1. Open your terminal or command prompt.

2. Navigate to the directory where you want to store the EcoFashion Hub website on your local device.

3. Clone the GitHub repository using the following command:

```
git clone https://github.com/your-username/EcoFashion-Hub.git
```

Replace `your-username` with your GitHub username.

## Setting up a Virtual Environment

1. Change into the cloned directory:

```
cd EcoFashion-Hub
```

2. Create a virtual environment:

```
python -m venv venv
```

3. Activate the virtual environment:

- On Windows:

```
venv\Scripts\activate
```

- On macOS and Linux:

```
source venv/bin/activate
```
</details>

## Running the Website

<details>

<summary><strong>Method 1: Using CodeSpaces</strong></summary>

If you are using GitHub CodeSpaces, follow these steps:

1. Open the `__init__.py` file in your CodeSpaces editor.

2. Click on the "Run" button at the top of the editor to start the development server.

3. Access the EcoFashion Hub website by clicking on the URL provided by the development server.

</details>

<details>

<summary><strong>Method 2: Using Python</strong></summary>

If you prefer to run the website using Python, follow these steps:

1. In your terminal or command prompt, make sure you are in the `EcoFashion-Hub` directory.

2. Run the following command to start the development server:

```
python __init__.py
```

3. Access the EcoFashion Hub website by visiting `http://localhost:5000` in your web browser.

</details>

## Stopping the Server

To stop the development server, press `Ctrl + C` in the terminal or command prompt where the server is running.

## UML
```mermaid
classDiagram
    class CustomerService {
        +int UserID
        +String TicketTitle
        +Date DateReceived
        +String Status
    }

    class Customer {
        +int UserID
        +String Name
        +String Email
        +String Gender
    }

    class Review {
        +int ProductID
        +int UserID
        +String Author
        +int Rating
        +String Description
    }

    class Product {
        +int ProductID
        +String Name
        +String Color
        +double CostPrice
        +double ListPrice
        +int Stock
        +String Description
        +String Category
    }

    class Order {
        +int OrderID
        +int UserID
        +int ProductID
        +Date OrderDate
        +String ShipTo
        +String PromoCode
    }

    class PromoCode {
        +String Code
        +double Discount
        +String Actions
    }

    CustomerService --|> Customer : User ID
    Customer --> Review : User ID
    Customer --> Order : User ID
    Review --|> Product : Product_ID
    Order --|> Product : Product_ID
    Order --> PromoCode : Promo Code
```

## Products
```mermaid
graph LR;
    A[Start] --> B(Explore Sustainable Fashion);
    B --> C(Add Items to Wishlist);
    C --> D(Review Wishlist and Proceed to Checkout);
    D --> E[Payment];
    E --> F{Payment Successful?};
    F --> |Yes| G[Order Confirmed];
    F --> |No| H[Payment Failed];
    G --> I[Delivery Process];
    I --> J[Delivered];
    I --> K[In Transit];
    I --> L[Out for Delivery];
    J --> M[Order Complete];
    K --> M;
    L --> M;
    H --> N[Order Cancelled];
    N --> O[Refund Process];
    O --> P[Refunded];
```
## Customer Service
```mermaid
flowchart LR;

    subgraph CustomerServiceFlow
        Start((Start))
        B(Customer Raises Inquiry)
        C((Resolution Required?))
        D[Resolve Inquiry]
        E[Escalate to Supervisor]
        F[Customer Satisfied]
        G[Issue Resolved]
        H[Supervisor Intervention]
        I[Investigation]
        J((Resolution Provided?))
        K[Proceed to Customer Feedback Collection]
        L[Identify Root Cause]
        M[Positive Feedback?]
        N[Negative Feedback?]
        O[Technical Issue]
        P[Communication Gap]
        Q[Process Gap]
        R[Share Positive Feedback with Customer]
        S((Compensation Required?))
        T[Apologize and Offer Discount]
        U[Issue Compensation]
        V[Seek Customer Preferences]
        W[Offer Discount]
        X[Provide Gift Voucher]
        Y[Product Replacement]
        Z[Refund Requested]
        End((End))
        
        Start -->|Raise Inquiry| B
        B -->|Resolution Required?| C
        C -->|Yes| D
        C -->|No| E
        D -->|Issue Resolved| G
        D -->|Customer Satisfied| F
        E -->|Supervisor Intervention| H
        H -->|Investigation| I
        I -->|Resolution Provided?| J
        J -->|Yes| K
        J -->|No| L
        K -->|Positive Feedback?| M
        K -->|Negative Feedback?| N
        L -->|Technical Issue| O
        L -->|Communication Gap| P
        L -->|Process Gap| Q
        M -->|Share Positive Feedback| R
        N -->|Compensation Required?| S
        N -->|Apologize and Offer Discount| T
        S -->|Issue Compensation| U
        S -->|Seek Customer Preferences| V
        U -->|Offer Discount| W
        U -->|Provide Gift Voucher| X
        V -->|Product Replacement| Y
        V -->|Refund Requested| Z
        R -->|End| End
        W -->|End| End
        X -->|End| End
        Y -->|End| End
        Z -->|End| End
        O -->|End| End
        P -->|End| End
        Q -->|End| End
        T -->|End| End
    end


```
## Account Management
```mermaid
graph LR;
    A[Start] --> B(Login to Account);
    B --> C{Correct Credentials?};
    C --> |Yes| D[Access Account Information];
    C --> |No| E[Incorrect Credentials];
    D --> F[View/Edit Account Details];
    D --> G[Change Password];
    F --> H[Save Changes];
    G --> H;
    B --> I[Create New Account];
    I --> J[Enter Account Information];
    J --> K[Submit Information];
    K --> L[Account Created];
```
## Conclusion

Congratulations! You have successfully set up and run the EcoFashion Hub website on your local device. You can now explore the website and enjoy its eco-friendly fashion offerings. Happy shopping!
