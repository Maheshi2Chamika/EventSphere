
// FastAPI backend URL
const API_URL = "http://127.0.0.1:8000";

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
        <p>Event ID: ${booking.event_id}</p>
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

            ticketCard.innerHTML = `
                <p><strong>Ticket Code:</strong></p>
                <p>${ticket.ticket_code}</p>
                <p>Status: ${ticket.is_checked_in ? "Checked In" : "Valid"}</p>
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

            ticketCard.innerHTML = `
                <p><strong>Ticket Code:</strong></p>
                <p>${ticket.ticket_code}</p>
                <p>Status: ${ticket.is_checked_in ? "Checked In" : "Valid"}</p>
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
