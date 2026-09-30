const API_URL = "/api";

const form =
  document.getElementById("task-form");

const message =
  document.getElementById("message");

const tasksContainer =
  document.getElementById("tasks");


async function loadTasks() {

  try {

    const response = await fetch(
      `${API_URL}/tasks`
    );

    const tasks = await response.json();

    tasksContainer.innerHTML = "";

    tasks.forEach((task) => {

      const element =
        document.createElement("div");

      element.className = "task";

      element.innerHTML = `
        <h3>${task.title}</h3>
        <p><strong>${task.name}</strong></p>
        <p>${task.email}</p>
        <p>${task.description}</p>
      `;

      tasksContainer.appendChild(
        element
      );
    });

  } catch (error) {

    console.error(
      "Erreur chargement tâches",
      error
    );
  }
}


form.addEventListener(
  "submit",
  async (event) => {

    event.preventDefault();

    const task = {
      name:
        document.getElementById("name")
          .value,

      email:
        document.getElementById("email")
          .value,

      title:
        document.getElementById("title")
          .value,

      description:
        document.getElementById(
          "description"
        ).value,
    };

    try {

      const response = await fetch(
        `${API_URL}/tasks`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify(task),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Erreur lors de la création"
        );
      }

      message.textContent =
        "Tâche enregistrée avec succès.";

      form.reset();

      await loadTasks();

    } catch (error) {

      message.textContent =
        "Erreur lors de l'enregistrement.";
    }
  }
);


loadTasks();