
//==============================================================================================//
// Classname:
//      CUDABasedRasterizationInput
//
//==============================================================================================//
// Description:
//      Data structure for the Cuda based rasterization
//
//==============================================================================================//

#pragma once

//==============================================================================================//

#include <cuda_runtime.h> 

//==============================================================================================//

#define THREADS_PER_BLOCK_CUDABASEDRASTERIZER 256

//==============================================================================================//

struct CUDABasedRasterizationInput
{
	//////////////////////////
	//CONSTANT INPUTS
	//////////////////////////

	//camera and frame
	int					numberOfCameras;						//number of cameras													//INIT IN CONSTRUCTOR
	float4*				d_cameraExtrinsics;						//camera extrinsics													//INIT IN CONSTRUCTOR
	float3*				d_cameraIntrinsics;						//camera intrinsics													//INIT IN CONSTRUCTOR
	int					w;										//frame width														//INIT IN CONSTRUCTOR
	int					h;										//frame height														//INIT IN CONSTRUCTOR

	//geometry
	int					F;										//number of faces													//INIT IN CONSTRUCTOR
	int					N;										//number of vertices												//INIT IN CONSTRUCTOR
	int3*				d_facesVertex;							//part of face data structure										//INIT IN CONSTRUCTOR

	//texture 
	float*				d_textureCoordinates;																						//INIT IN CONSTRUCTOR

	//////////////////////////
	//STATES 
	//////////////////////////

	//misc
	int4*				d_BBoxes;								//bbox for each triangle											//INIT IN CONSTRUCTOR
	float3*				d_projectedVertices;					//vertex position on image with depth after projection				//INIT IN CONSTRUCTOR

	//////////////////////////
	//INPUTS
	//////////////////////////

	float3*				d_vertices;								//vertex positions
	float3*				d_vertexColor;							//vertex color

	//texture
	int					texWidth;								//dimension of texture
	int					texHeight;								//dimension of texture
	const float*		d_textureMap;							//texture map

	//////////////////////////
	//OUTPUT 
	//////////////////////////

	//render buffers
	int*				d_faceIDBuffer;							//face ID per pixel per view and the ids of the 3 vertices
	int*				d_depthBuffer;							//depth value per pixel per view
	float*				d_barycentricCoordinatesBuffer;			//barycentric coordinates per pixel per view
	float*				d_renderBuffer;
	float*				d_vertexColorBuffer;

	//visibility and boundary per vertex
	bool*				d_visibilities;							//is visible flag (per vertex per view)
	bool*				d_boundaries;							//is boundary flag (per vertex per view)

	
};