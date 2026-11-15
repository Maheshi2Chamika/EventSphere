
// FastAPI backend URL
const API_URL = window.location.origin;

// Load events from the backend
async function loadEvents() {
    const eventList = document.getElementById("event-list");

    try {
        const response = await fetch(`${API_URL}/events`);

        if (!response.ok) {
            throw new Error("Failed to load events");
        }

        const events = await response.json();

        eventList.innerHTML = "";

        if (events.length === 0) {
            eventList.innerHTML = "<p>No events available.</p>";
            return;
        }

        events.forEach(event => {
            const card = document.createElement("div");
            card.className = "event-card";

            card.innerHTML = `
                <h3>${event.title}</h3>
                <p>${event.description || "No description available"}</p>
                <p><strong>Date:</strong> ${new Date(event.event_date).toLocaleString()}</p>
                <p><strong>Status:</strong> ${event.status}</p>
            `;

            eventList.appendChild(card);
        });

    } catch (error) {
        eventList.innerHTML = "<p>Unable to load events. Please check the backend.</p>";
        console.error(error);
    }
}


// Load available venues from the backend
async function loadVenues() {
    const venueList = document.getElementById("venue-list");

    try {
        const response = await fetch(`${API_URL}/venues`);

        if (!response.ok) {
            throw new Error("Failed to load venues");
        }

        const venues = await response.json();

        venueList.innerHTML = "";

        if (venues.length === 0) {
            venueList.innerHTML = "<p>No venues available.</p>";
            return;
        }

        venues.forEach(venue => {
            const card = document.createElement("div");
            card.className = "venue-card";

            card.innerHTML = `
                <h3>${venue.name}</h3>
                <p><strong>Location:</strong> ${venue.location}</p>
                <p><strong>Capacity:</strong> ${venue.capacity}</p>
                <p>${venue.description || ""}</p>
            `;

            venueList.appendChild(card);
        });

    } catch (error) {
        venueList.innerHTML = "<p>Unable to load venues. Please check the backend.</p>";
        console.error(error);
    }
}


// Load data when the page opens
document.addEventListener("DOMContentLoaded", () => {
    loadEvents();
    loadVenues();
    loadNotifications();
    loadVenueHireRequests();
});



// Load events into the booking form
async function loadBookingEvents() {
    const eventSelect = document.getElementById("event-id");

    try {
        const response = await fetch(`${API_URL}/events`);
        const events = await response.json();

        events.forEach(event => {
            const option = document.createElement("option");
            option.value = event.id;
            option.textContent = event.title;
            eventSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading booking events:", error);
    }
}


// Load ticket categories when an event is selected
async function loadTicketCategories() {
    const eventId = document.getElementById("event-id").value;
    const categorySelect = document.getElementById("category-id");

    categorySelect.innerHTML =
        '<option value="">Select a category</option>';

    if (!eventId) return;

    try {
        const response = await fetch(`${API_URL}/ticket-categories`);
        const categories = await response.json();

        categories
            .filter(category => category.event_id == eventId)
            .forEach(category => {
                const option = document.createElement("option");
                option.value = category.id;
                option.textContent =
                    `${category.name} - LKR ${category.price} (${category.quantity} available)`;

                categorySelect.appendChild(option);
            });

    } catch (error) {
        console.error("Error loading ticket categories:", error);
    }
}


// Submit a ticket booking
async function createBooking(event) {
    event.preventDefault();

    const bookingData = {
        user_id: Number(document.getElementById("user-id").value),
        event_id: Number(document.getElementById("event-id").value),
        ticket_category_id: Number(document.getElementById("category-id").value),
        quantity: Number(document.getElementById("quantity").value)
    };

    const message = document.getElementById("booking-message");

    try {
        const response = await fetch(`${API_URL}/bookings`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(bookingData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Booking failed");
        }

        message.textContent =
            `Booking successful! Booking ID: ${result.id}. Total: LKR ${result.total_price}`;

        document.getElementById("booking-form").reset();

        await loadMyBookings();
        await loadTicketCategories();
        await loadNotifications();

    } catch (error) {
        message.textContent = error.message;
    }
}


// Load bookings
async function loadMyBookings() {
    const bookingList = document.getElementById("booking-list");

    try {
        const response = await fetch(`${API_URL}/bookings`);
const bookings = await response.json();

// Get event details
    const eventResponse = await fetch(`${API_URL}/events`);
    const events = await eventResponse.json();

    // Create an event ID-to-name lookup
    const eventNames = {};

    events.forEach(event => {
        eventNames[event.id] = event.title;
    });

        bookingList.innerHTML = "";

        const userId = Number(document.getElementById("user-id").value);

        const userBookings = bookings.filter(
            booking => booking.user_id === userId
        );

        if (userBookings.length === 0) {
            bookingList.textContent = "No bookings yet.";
            return;
        }

        
userBookings.forEach(booking => {
    const card = document.createElement("div");
    card.className = "event-card";

    card.innerHTML = `
        <h3>Booking #${booking.id}</h3>
        <p>Event: ${eventNames[booking.event_id] || "Unknown Event"}</p>
        <p>Quantity: ${booking.quantity}</p>
        <p>Total: LKR ${booking.total_price}</p>
        <p>Status: ${booking.status}</p>

        <button class="generate-ticket-btn"
                data-booking-id="${booking.id}">
            Generate Digital Tickets
        </button>

        <div id="tickets-${booking.id}"></div>
    `;

    bookingList.appendChild(card);

    const button = card.querySelector(".generate-ticket-btn");

    // Load previously generated tickets
    loadExistingTickets(booking.id, button);

    button.addEventListener("click", () => {
        generateDigitalTickets(booking.id, button);
    });
});


    } catch (error) {
        bookingList.textContent = "Unable to load bookings.";
        console.error(error);
    }
}


// Connect booking form events
document.addEventListener("DOMContentLoaded", () => {
    loadBookingEvents();
    loadMyBookings();

    document.getElementById("event-id")
        .addEventListener("change", loadTicketCategories);

    document.getElementById("booking-form")
        .addEventListener("submit", createBooking);
});

// Load existing digital tickets for a booking
async function loadExistingTickets(bookingId, button) {
    const ticketContainer =
        document.getElementById(`tickets-${bookingId}`);

    try {
        const response = await fetch(
            `${API_URL}/bookings/${bookingId}/tickets`
        );

        if (!response.ok) {
            throw new Error("Failed to load existing tickets");
        }

        const tickets = await response.json();

        ticketContainer.innerHTML = "";

        if (tickets.length === 0) {
            ticketContainer.textContent =
                "No digital tickets generated yet.";
            return;
        }

        ticketContainer.innerHTML =
            "<h4>Your Digital Tickets</h4>";

        tickets.forEach(ticket => {
           const ticketCard = document.createElement("div");
           ticketCard.className = "ticket-card";
           ticketCard.dataset.ticketCode = ticket.ticket_code;

            ticketCard.innerHTML = `
                <p><strong>Ticket Code:</strong></p>
                <p>${ticket.ticket_code}</p>
                <p>Status: <span class="ticket-status">${ticket.is_checked_in ? "Checked In" : "Valid"}</span></p>
            `;

            ticketContainer.appendChild(ticketCard);
        });

        button.textContent = "Tickets Generated";
        button.disabled = true;

    } catch (error) {
        console.error("Error loading existing tickets:", error);
    }
}

async function generateDigitalTickets(bookingId, button) {

    const ticketContainer =
        document.getElementById(`tickets-${bookingId}`);

    button.disabled = true;
    button.textContent = "Generating...";

    try {
        const response = await fetch(
            `${API_URL}/bookings/${bookingId}/tickets`,
            {
                method: "POST"
            }
        );

        const tickets = await response.json();

        if (!response.ok) {
            throw new Error(tickets.detail || "Ticket generation failed");
        }

        ticketContainer.innerHTML = "<h4>Your Digital Tickets</h4>";

        tickets.forEach(ticket => {
            const ticketCard = document.createElement("div");
            ticketCard.className = "ticket-card";
            ticketCard.dataset.ticketCode = ticket.ticket_code;

            ticketCard.innerHTML = `
                <p><strong>Ticket Code:</strong></p>
                <p>${ticket.ticket_code}</p>
                <p>Status: <span class="ticket-status">${ticket.is_checked_in ? "Checked In" : "Valid"}</span></p>
            `;

            ticketContainer.appendChild(ticketCard);
        });

        button.textContent = "Tickets Generated";

    } catch (error) {
        ticketContainer.textContent = error.message;
        button.disabled = false;
        button.textContent = "Generate Digital Tickets";
    }
}



// Validate a digital ticket
async function checkInTicket(event) {
    event.preventDefault();

    const ticketCode =
        document.getElementById("ticket-code").value.trim();

    const message =
        document.getElementById("checkin-message");

    try {
        const response = await fetch(
            `${API_URL}/tickets/${encodeURIComponent(ticketCode)}/check-in`,
            {
                method: "POST"
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Ticket validation failed");
        }

        message.textContent =
    "Ticket successfully checked in!";

// Update the ticket status without refreshing
document.querySelectorAll(".ticket-card").forEach(card => {
    if (card.dataset.ticketCode === ticketCode) {
        const status = card.querySelector(".ticket-status");

        if (status) {
            status.textContent = "Checked In";
        }
    }
});

        document.getElementById("checkin-form").reset();

    } catch (error) {
        message.textContent = error.message;
    }
}


// Connect the check-in form
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("checkin-form")
        .addEventListener("submit", checkInTicket);
});



// Load notifications for the current user
async function loadNotifications() {
    const notificationList =
        document.getElementById("notification-list");

    const userId =
        Number(document.getElementById("user-id").value);

    try {
        const response = await fetch(
            `${API_URL}/notifications/${userId}`
        );

        if (!response.ok) {
            throw new Error("Failed to load notifications");
        }

        const notifications = await response.json();

        notificationList.innerHTML = "";

        if (notifications.length === 0) {
            notificationList.textContent = "No notifications yet.";
            return;
        }

        notifications.forEach(notification => {
            const card = document.createElement("div");
            card.className = "event-card";

            const title = document.createElement("h3");
            title.textContent = notification.title;

            const message = document.createElement("p");
            message.textContent = notification.message;

            const status = document.createElement("p");
            status.textContent = notification.is_read
                ? "Read"
                : "Unread";

            card.appendChild(title);
            card.appendChild(message);
            card.appendChild(status);

            if (!notification.is_read) {
                const button = document.createElement("button");
                button.textContent = "Mark as Read";

                button.addEventListener("click", () => {
                    markNotificationAsRead(
                        notification.id
                    );
                });

                card.appendChild(button);
            }

            notificationList.appendChild(card);
        });

    } catch (error) {
        notificationList.textContent =
            "Unable to load notifications.";

        console.error(error);
    }
}


// Mark a notification as read
async function markNotificationAsRead(notificationId) {
    try {
        const response = await fetch(
            `${API_URL}/notifications/${notificationId}/read`,
            {
                method: "PUT"
            }
        );

        if (!response.ok) {
            throw new Error("Failed to update notification");
        }

        await loadNotifications();

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}



// Load all waitlist messages
async function loadWaitlist() {
    const waitlistList =
        document.getElementById("waitlist-list");

    try {
        const response = await fetch(`${API_URL}/waitlist`);

        if (!response.ok) {
            throw new Error("Failed to load waitlist");
        }

        const messages = await response.json();

        waitlistList.innerHTML = "";

        if (messages.length === 0) {
            waitlistList.textContent = "No waitlist messages yet.";
            return;
        }

        messages.forEach(item => {
            const card = document.createElement("div");
            card.className = "event-card";

            const heading = document.createElement("h3");
            heading.textContent = `Waitlist Message #${item.id}`;

            const user = document.createElement("p");
            user.textContent = `User ID: ${item.user_id}`;

            const message = document.createElement("p");
            message.textContent = item.message_text;

            card.appendChild(heading);
            card.appendChild(user);
            card.appendChild(message);

            waitlistList.appendChild(card);
        });

    } catch (error) {
        waitlistList.textContent =
            "Unable to load waitlist messages.";

        console.error(error);
    }
}


// Submit a waitlist message
async function submitWaitlistMessage(event) {
    event.preventDefault();

    const userId = Number(
        document.getElementById("waitlist-user-id").value
    );

    const messageText =
        document.getElementById("waitlist-message").value.trim();

    const responseMessage =
        document.getElementById("waitlist-response");

    if (!messageText) {
        responseMessage.textContent = "Please enter a message.";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/waitlist`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                message_text: messageText
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Failed to join waitlist");
        }

        responseMessage.textContent =
            "Successfully joined the waitlist!";

        document.getElementById("waitlist-form").reset();

        // Restore default user ID
        document.getElementById("waitlist-user-id").value = 1;

        // Refresh waitlist messages
        await loadWaitlist();

    } catch (error) {
        responseMessage.textContent = error.message;
        console.error(error);
    }
}


// Connect waitlist form
document.addEventListener("DOMContentLoaded", () => {

    loadWaitlist();

    document.getElementById("waitlist-form")
        .addEventListener("submit", submitWaitlistMessage);

});


// Submit a venue hire request
async function submitVenueHireRequest(event) {
    event.preventDefault();

    const userId = Number(
        document.getElementById("hire-user-id").value
    );

    const venueId = Number(
        document.getElementById("hire-venue-id").value
    );

    const eventName = document.getElementById("hire-event-name").value.trim();

    const requestedDate = document.getElementById("hire-date").value;

    const expectedAttendees = Number(
        document.getElementById("hire-attendees").value
    );

    const responseMessage = document.getElementById(
        "venue-hire-response"
    );

    try {
        const response = await fetch(`${API_URL}/venue-hire-requests`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                venue_id: venueId,
                event_name: eventName,
                requested_date: requestedDate,
                expected_attendees: expectedAttendees
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Failed to submit venue hire request."
            );
        }

        responseMessage.textContent =
            "Venue hire request submitted successfully!";

        document.getElementById("venue-hire-form").reset();

        document.getElementById("hire-user-id").value = 1;

        // Refresh the venue hire request list
        await loadVenueHireRequests();
    } catch (error) {
        responseMessage.textContent = error.message;
        console.error(error);
    }
}

// Connect the form
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("venue-hire-form")
        .addEventListener("submit", submitVenueHireRequest);
});

// Load all venue hire requests
async function loadVenueHireRequests() {
    const requestList = document.getElementById("venue-hire-list");

    try {
        const response = await fetch(`${API_URL}/venue-hire-requests`);

        if (!response.ok) {
            throw new Error("Failed to load venue hire requests");
        }

        const requests = await response.json();

        requestList.innerHTML = "";

        if (requests.length === 0) {
            requestList.textContent = "No venue hire requests yet.";
            return;
        }

        requests.forEach(request => {
            const card = document.createElement("div");
            card.className = "event-card";

            card.innerHTML = `
                <h3>Request #${request.id}</h3>
                <p>User ID: ${request.user_id}</p>
                <p>Venue ID: ${request.venue_id}</p>
                <p>Event: ${request.event_name}</p>
                <p>Date: ${new Date(request.requested_date).toLocaleString()}</p>
                <p>Expected Attendees: ${request.expected_attendees}</p>
                <p>Status: ${request.status}</p>
            `;

            requestList.appendChild(card);
        });

    } catch (error) {
        requestList.textContent = error.message;
        console.error(error);
    }
}