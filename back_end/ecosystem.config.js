module.exports = {
    apps: [
        {
            name: "Server",
            script: "make run",
            watch: true
        },
        {
            name: "Tika Server",
            script: "make run_tika_dev",
            watch: true
        },
        {
            name: "Job Queue",
            script: "make run_job_q",
            watch: true
        }
    ],
};
