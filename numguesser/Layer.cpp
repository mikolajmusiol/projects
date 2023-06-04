#include <vector>

#include "classes.h"

class Layer
{
private:
	//std::vector<double> neurons;
	std::vector<std::vector<double>> neurons;
	//std::vector<double> derivedNeurons;
public:
	double sigmoid(const double& neuron)
	{
		return 1 / (1 + exp(neuron));
	}
	double sigmoidDerivative(const double& neuron)
	{
		return sigmoid(neuron) * (1 - sigmoid(neuron));
	}
	/*
	void derNeurons()
	{
		for (auto i : neurons)
		{
			derivedNeurons.push_back(sigmoidDerivative(i));
		}
	}
	*/

	////modify&return
	/*
	void modify_Neurons(const std::vector<double>& newNeurons)
	{
		neurons.clear();
		neurons = newNeurons;
	}
	std::vector<double> return_Neurons()
	{
		return neurons;
	}
	*/
	
	void modify_Neurons(const int& index, const std::vector<double>& newNeurons)
	{
		neurons[index] = newNeurons;
	}
	void add_Neurons(const std::vector<double>& newNeurons)
	{
		neurons.push_back(newNeurons);
	}
	std::vector<double> return_Neurons(const int& index)
	{
		return neurons[index];
	}
	std::vector<std::vector<double>> return_allNeurons()
	{
		return neurons;
	}
	void kill_neurons()
	{
		neurons.clear();
	}
};