from fastapi import FastAPI, APIRouter, Query, HTTPException, BackgroundTasks
from loguru import logger
from uvicorn import run
from datetime import datetime
import uuid

from webScraping import scrape_sunway_pyramid_directory
from googleScraping import get_mall_info

app = FastAPI()
router = APIRouter()

# Configure logger
logger.add(
    "logger.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 MB",
)

# Store task statuses
class TaskManager:
    def __init__(self):
        self.task_statuses = {}

    def set_task_status(self, task_id: str, status: str, details: str = ""):
        self.task_statuses[task_id] = {
            "status": status,
            "details": details,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_task_status(self, task_id: str):
        return self.task_statuses.get(task_id, {"status": "unknown"})
    
    def get_all_task_statuses(self):
        return self.task_statuses

manager = TaskManager()



def execute_scraping_task(
    task_id: str,
):
    try:
        # Update and notify task started
        manager.set_task_status(task_id, "running", "Scraping execution started")
     
        scrape_sunway_pyramid_directory()
        # Update task status
        manager.set_task_status(task_id, "completed", "Scraping executed successfully")
        
        logger.info(f"Successfully generated and saved data to the table for Scraping")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in Scraping task {task_id}: {error_msg}")
        
        # Update and notify task failed
        manager.set_task_status(task_id, "failed", f"Error: {error_msg}")
        raise


@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/start-scraping")
async def start_scraping(
        background_tasks: BackgroundTasks,

):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(execute_scraping_task, task_id)
    
    return {
        "message": "Scraping task started in the background", 
        "task_id": task_id
    }

@app.get("/tasks")
async def get_all_tasks():
    task_statuses = manager.get_all_task_statuses()
    return {"tasks": [{"task_id": k, **v} for k, v in task_statuses.items()]}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    return manager.get_task_status(task_id)


@app.get("/google")
async def get_all_tasks():
    get_mall_info('Empotium Mall')
    return {"message":'succesfull'}


if __name__ == "__main__":
    run(
        app, host="0.0.0.0", port=8000
    )
