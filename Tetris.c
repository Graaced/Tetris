#include "raylib.h"
#include <time.h>
#include <string.h>

// CREATE THE PLAYING FIELD

#define STAGE_WIDTH 12
#define STAGE_HEIGHT 22
#define TILE_SIZE 16
#define TETROMINO_SIZE 4

//TILE MAP to REPRESENT OUR LEVEL
// 0 empty 1 wall
int stage[] = 
{
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
};

// L

// ROTATION AT 0
const int lTetromino0[] =
{
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 1, 1, 0,
    0, 0, 0, 0,
};
// ROTATION AT 90
const int lTetromino90[] =
{
    0, 0, 0, 0,
    1, 1, 1, 0,
    1, 0, 0, 0,
    0, 0, 0, 0,
};
// ROTATION AT 180
const int lTetromino180[] =
{
    1, 1, 0, 0,
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 0, 0, 0,
};
// ROTATION AT 270
const int lTetromino270[] =
{
    0, 0, 1, 0,
    1, 1, 1, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
};

// J
const int jTetromino0[] =
{
    0, 1, 0, 0,
    0, 1, 0, 0,
    1, 1, 0, 0,
    0, 0, 0, 0,
};

const int jTetromino90[] =
{
    1, 0, 0, 0,
    1, 1, 1, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
};

const int jTetromino180[] =
{
    0, 1, 1, 0,
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 0, 0, 0,
};

const int jTetromino270[] =
{
    0, 0, 0, 0,
    1, 1, 1, 0,
    0, 0, 1, 0,
    0, 0, 0, 0,
};

// O
const int oTetromino[] =
{
    1, 1, 0, 0,
    1, 1, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
};

// S
const int sTetromino0[] =
{
    0, 0, 0, 0,
    0, 1, 1, 0,
    1, 1, 0, 0,
    0, 0, 0, 0,
};

const int sTetromino90[] =
{
    0, 0, 0, 0,
    0, 1, 0, 0,
    0, 1, 1, 0,
    0, 0, 1, 0,
};

const int sTetromino180[] =
{
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 1, 1, 0,
    1, 1, 0, 0,
};

const int sTetromino270[] =
{
    0, 0, 0, 0,
    1, 0, 0, 0,
    1, 1, 0, 0,
    0, 1, 0, 0,
};

// T
const int tTetromino0[] =
{
    0, 0, 0, 0,
    1, 1, 1, 0,
    0, 1, 0, 0,
    0, 0, 0, 0,
};

const int tTetromino90[] =
{
    0, 1, 0, 0,
    1, 1, 0, 0,
    0, 1, 0, 0,
    0, 0, 0, 0,
};

const int tTetromino180[] =
{
    0, 1, 0, 0,
    1, 1, 1, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
};

const int tTetromino270[] =
{
    1, 0, 0, 0,
    1, 1, 0, 0,
    1, 0, 0, 0,
    0, 0, 0, 0,
};

// I
const int iTetromino0[] =
{
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 1, 0, 0,
};

const int iTetromino90[] =
{
    0, 0, 0, 0,
    1, 1, 1, 1,
    0, 0, 0, 0,
    0, 0, 0, 0,
};

const int iTetromino180[] =
{
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 1, 0, 0,
    0, 1, 0, 0,
};

const int iTetromino270[] =
{
    0, 0, 0, 0,
    1, 1, 1, 1,
    0, 0, 0, 0,
    0, 0, 0, 0,
};

// Z
const int zTetromino0[] =
{
    0, 0, 0, 0,
    1, 1, 0, 0,
    0, 1, 1, 0,
    0, 0, 0, 0,
};

const int zTetromino90[] =
{
    0, 1, 0, 0,
    0, 1, 1, 0,
    0, 0, 1, 0,
    0, 0, 0, 0,
};

const int zTetromino180[] =
{
    0, 0, 0, 0,
    0, 1, 1, 0,
    1, 1, 0, 0,
    0, 0, 0, 0,
};

const int zTetromino270[] =
{
    1, 0, 0, 0,
    1, 1, 0, 0,
    0, 1, 0, 0,
    0, 0, 0, 0,
};


const Color colorTypes[8] =
{
    {255,255,85,255},
    {85,43,158,255},
    {56,255,85,255},
    {255,255,63,255},
    {255,42,85,255},
    {255,100,85,255},
    {97,5,85,255},
    {85,45,63,255},
};

// make an array of arrays for each tetromino to be able to move from one tetromino in one position to another 
const int *tetrominoTypes[7][4] =
{
    {zTetromino0, zTetromino90, zTetromino180, zTetromino270},
    {sTetromino0, sTetromino90, sTetromino180, sTetromino270},
    {tTetromino0, tTetromino90, tTetromino180, tTetromino270},
    {oTetromino, oTetromino, oTetromino, oTetromino},
    {iTetromino0, iTetromino90, iTetromino180, iTetromino270},
    {jTetromino0, jTetromino90, jTetromino180, jTetromino270},
    {lTetromino0, lTetromino90, lTetromino180, lTetromino270},
};

int CheckCollision(const int tetrominoStartX, const int tetrominoStartY, const int *tetromino)
{
    for (int y = 0; y < TETROMINO_SIZE; y++)
    {
        for (int x = 0; x < TETROMINO_SIZE; x++)
        {
            const int offset = y * TETROMINO_SIZE + x;

            if (tetromino[offset] == 1)
            {
               const int offset_stage = (y + tetrominoStartY) * STAGE_WIDTH + (x + tetrominoStartX);

               if (stage[offset_stage] != 0)
               {
                    return 1;
               }
               
            }
            
        }
        
    }

    return 0;
    
}

void drawTetromino(const Color currentColor, const int startOffsetX, const int startOffsetY, const int tetrominoStartX, const int tetrominoStartY, const int *tetromino)
{
    for(int y = 0; y < TETROMINO_SIZE; y++)
    {
        for(int x = 0; x < TETROMINO_SIZE; x++)
        {
            const int offset = y * TETROMINO_SIZE + x; 

            if(tetromino[offset] == 1)
            {
                DrawRectangle((x + tetrominoStartX) * TILE_SIZE + startOffsetX, (y + tetrominoStartY) * TILE_SIZE + startOffsetY, TILE_SIZE, TILE_SIZE, currentColor);
            }
        }
    }
}

void ResetLines(int startLineY) 
{
    /*after having eliminated the last line, I lower the remaining pieces;
    after cleaning the line, I have to take all the pieces that are above the line that has been eliminated and
    move them down 1 */

    for (int y = startLineY; y >= 0; y--)
    {
        for (int x = 1; x < STAGE_WIDTH - 1; x++)
        {
            const int offset = y * STAGE_WIDTH + x; 
            const int offset_below = (y+1) * STAGE_WIDTH + x;  

            if (stage[offset_below] == 0 && stage[offset] > 0) // if the piece below is equal to 0 and the piece above is greater than 0
            {
                // the top piece can go down to the offset of the bottom one
                stage[offset_below] = stage[offset];
                stage[offset] = 0;
            }
        }
    }   
    
}



// SCORE 
int score = 0;
float moveTetrominoDownTimer = 1;
int maxpoints = 200;
int soundAlreadyPlayed = 0;

// SOUND
Sound clearLineSound;
Sound incrementSpeedGapSound;



void DeleteLines()
{
    
    for (int y = 0; y < STAGE_HEIGHT - 1; y++)
    {
        int checkLine = 1; 

        for (int x = 1; x < STAGE_WIDTH - 1; x++)
        {
            const int offset = y * STAGE_WIDTH + x;

            if (stage[offset] == 0) 
            {
                checkLine = 0; 
                break; 
            }
        }

        if(checkLine) // if the line is full I delete it
        {
            const int offset = y * STAGE_WIDTH + 1;
            memset(stage+offset,0,(STAGE_WIDTH-2)* sizeof(int));

            ResetLines(y);

            score += 100; // Increment the score when a row is deleted

            PlaySound(clearLineSound);
        }

        // increase the score to increase the speed of the tetromino
        if (score >= maxpoints && !soundAlreadyPlayed)
        {
            moveTetrominoDownTimer -= 0.1;
            maxpoints += 200;

            PlaySound(incrementSpeedGapSound);

            soundAlreadyPlayed = 1;
        }
        
        soundAlreadyPlayed = 0;
        
    }   
}


int main(int argc, char **argv, char **environ)
{
    // WINDOW SIZE
    const int windowWidth = 512; 
    const int windowHeight = 512; 

    // setting the square in the center of the screen
    const int startOffsetX = (windowWidth / 2) - ((STAGE_WIDTH * TILE_SIZE) / 2); 
    const int startOffsetY = (windowHeight / 2) - ((STAGE_HEIGHT * TILE_SIZE) / 2);

    // TETROMINO CREATE
    const int tetrominoStartX = STAGE_WIDTH / 2;
    const int tetrominoStartY = 0;  

    int currentTetrominoX = tetrominoStartX;
    int currentTetrominoY = tetrominoStartY;

    time_t unixTime;

    time(&unixTime);

   // initialize the seed that will appear 
   // SetRandomSeed() is used to initialize the random number generator
    SetRandomSeed(unixTime);

    int currentTetrominoType = GetRandomValue(0, 6);
    int currentRotation = 0;

    
    // TIMER SPAWN TETROMINO
    float timeToMoveTetrominoDown = moveTetrominoDownTimer;
    int currentColor = GetRandomValue(0, 7);

    // GRAPHICS
    InitWindow(windowWidth, windowHeight, "Tetris");

    //AUDIO
    InitAudioDevice();
    clearLineSound = LoadSound("clear.wav");
    incrementSpeedGapSound = LoadSound("success.wav");

    SetTargetFPS(60);

    while(!WindowShouldClose())
    {

        timeToMoveTetrominoDown -= GetFrameTime();

        // ROTATION KEY 
        if (IsKeyPressed(KEY_SPACE))
        {
            const int lastRotation = currentRotation;

            currentRotation++;

            if (currentRotation > 3)
            {
                currentRotation = 0;
            }

            if (CheckCollision(currentTetrominoX,currentTetrominoY,tetrominoTypes[currentTetrominoType][currentRotation]))
            {
                currentRotation = lastRotation;
                
            }
        }

       if (IsKeyPressed(KEY_RIGHT))
        {
            // No need to check overflow, wall is your protector
            if (!CheckCollision(currentTetrominoX+1,currentTetrominoY,tetrominoTypes[currentTetrominoType][currentRotation]))
            {
                currentTetrominoX++;
                
            }
        }
        if (IsKeyPressed(KEY_LEFT))
        {
            // No need to check overflow, wall is your protector
            if (!CheckCollision(currentTetrominoX-1,currentTetrominoY,tetrominoTypes[currentTetrominoType][currentRotation]))
            {
                currentTetrominoX--;
                
            }
        }
        
        if(timeToMoveTetrominoDown <= 0 || IsKeyPressed(KEY_DOWN)) // when I press the key it makes time pass faster, therefore the piece will progress faster
        {            
            if(!CheckCollision(currentTetrominoX,currentTetrominoY+1,tetrominoTypes[currentTetrominoType][currentRotation]))
            {
                
                currentTetrominoY++;
                timeToMoveTetrominoDown = moveTetrominoDownTimer; 
                   
            }

            else
            {

                for(int y = 0; y < TETROMINO_SIZE; y++)
                {
                    for(int x = 0; x < TETROMINO_SIZE; x++)
                    {
                        const int offset = y * TETROMINO_SIZE + x;

                        const int *tetromino = tetrominoTypes[currentTetrominoType][currentRotation];

                        if(tetromino[offset] == 1)
                        {
                            const int offset_stage = (y + currentTetrominoY) * STAGE_WIDTH + (x + currentTetrominoX);

                            stage[offset_stage] = currentColor+1;
                        }
                    }
                }

                // REMOVE LINES
                DeleteLines();


                // BRING THE TETRAMINO BACK TO ITS Y
                currentTetrominoX = tetrominoStartX;
                currentTetrominoY = tetrominoStartY;

                currentTetrominoType = GetRandomValue(0, 6);
                currentRotation = 0;
                currentColor = GetRandomValue(0, 7);

            }
        }

        // CLEAR
        BeginDrawing();
        ClearBackground(RED);
        
        // SQUADRE DRAW  
        for(int y = 0; y < STAGE_HEIGHT; y++)
        {
            for(int x = 0; x < STAGE_WIDTH; x++)
            {
                const int offset = y * STAGE_WIDTH + x; 

                if(stage[offset] >= 1)
                {
                    DrawRectangle(x * TILE_SIZE + startOffsetX, y * TILE_SIZE + startOffsetY, TILE_SIZE, TILE_SIZE, WHITE);
                }

                // I DRAW THE BLACK OUTLINE FOR EACH CELL
                DrawRectangleLines(x * TILE_SIZE + startOffsetX, y * TILE_SIZE + startOffsetY, TILE_SIZE, TILE_SIZE, BLACK);
            }
        }

        // TETRAMINO DRAW
        drawTetromino(colorTypes[currentColor],startOffsetX, startOffsetY, currentTetrominoX, currentTetrominoY, tetrominoTypes[currentTetrominoType][currentRotation]);

        // SCORE DRAW
        DrawText(TextFormat("Score : %d", score), 10, 10, 20,WHITE); 

        EndDrawing();
    }

    
    return 0;                                             
}