#triangleIntersection.py
"""
Jens V Hansen 
jensvhansen.com

A triangle class primaily written to check the distance between point 'q' and triangle 'n'.
Which is why the functions return True or False instead of numeric values as in distances.

A basic implementation of a 3D vector is needed to use the clasees.
"""
# import 'myVector' as Veector3 
from sys import maxint

global MAX = maxint() 

class Edge(object):
    def __init__(self, v0, v1):
        """
        Structure to hold the references of the edge.
        """
        # edge vertices
        self.v0 = v0
        self.v1 = v1
        
        # edge vector
        self.ev = self.v1 - self.v0
        
    def normal(self):
        return self.ev.normal()
    
    def length(self):
        return self.ev.length()
    
class Triangle(object):
    def __init__(self, v0, v1, v2):
        """
        Representation of a triangle formed by three vertices.
        The object holds a reference to the vertices and edges 
        
        Assumes a basic vector class is implemented with operator overload:
        ^ = cross product between two vectors.
        * = dot product between two vectors.
        
        .normal() = returns a normalized version of the vector.
        .length() = returns the length of the vector in scalar value.
        """
        # Hold a reference to the vertices forming the triangle.
        self.v0, self.v1, self.v2 = v0,v1,v2
        
        # Calculate the edges of the triangle.
        self.edges = (Edge(self.v0, self.v1),
                      Edge(self.v1, self.v2),
                      Edge(self.v0, self.v2))
        
        
        # Unit normal of the triangle.
        # Computed by the cross product of two of the edges then normalized.
        self.normal = (self.edges[2].ev ^ self.edges[0].ev).normal() 
        
        # 'd' value of the plane.
        # Dot product of a vertex of the triangle and the normal of the triangle.
        self.d = self.v0 * self.normal
        
    def barycentric(self, ip):
        """
        Determinate the barycentric coordinate of a point relative to the triangle.
        The point must lie on the plane formed by the triangle, hence a intersection point is needed.
        http://realtimecollisiondetection.net/
        http://gamedev.stackexchange.com/questions/23743/whats-the-most-efficient-way-to-find-barycentric-coordinates 
        """
        v0 = self.edges[2].ev
        v1 = self.edges[0].ev
        v2 = Vector3(ip - Vector3(self.v0))
    
        
        d00 = v0 * v0
        d01 = v0 * v1
        d11 = v1 * v1
        d20 = v2 * v0
        d21 = v2 * v1
        
        denom = d00 * d11 - d01 * d01
        
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w
        return (v, w, u)

    def examineBaryCord(self, baryCord):
        """
        Analyzes the Barycentric coordinate to determine if its 
        inside the triangle, if not check which component its closest 
        to, e.g. vertex or edge. 
        
        return values:
        edge id's:                        0,1,2
        point is within, i.e. True:       3
        point is closer to a vertex:      4
        """
    
        # Check the weightings of the the barycentric coordinate.
        # Count how many weightings are negative.
        negativeWeightings = sum(n < 0 for n in baryCord)
        
        # If there are no negative values the barycentric coordinate
        # is within the triangle.
        if negativeWeightings == 0:
            return 3
        
        # If there is only one negative weighting the coordinate is 
        # closer to edge 'n' than anything else. 
        elif negativeWeightings == 1:
            # return the index of the closest edge.
            return baryCord.index(min(baryCord))

        
        # If two negative weightings the coordinate is closer 
        # to vertex 'n' than anything else.
        elif negativeWeightings == 2:
            return 4
    
    
    def distanceToEdge(self, edgeId, pointQ):
        """
        3D Math primer for Graphics and Game Development
        p. 718 'Closest point on a parametric ray'
        
        """
        # Define a parametric ray of the edge in question.
        
        # 'd' value of the ray.
        dUnit = self.edges[edgeId].normal()
        
        # Length of the ray if you displace the unit vector of the ray by l.
        l = self.edges[edgeId].length()
        
        # Vector from to the origin of the parametric ray to 'pointQ'.
        pToRay = pointQ - Vector3(self.edges[edgeId].v0)
        
        # The displacement if you go along the ray from its origin point
        # until you get to the intersection on the ray that is perpendicular 
        # to the point to check against.
        t = dUnit * pToRay
        
        # If t > 0 the intersection point of 'pointQ' happens before
        # the origin point on the parametric ray.
        # If t < l the intersection is beyond the 'end' point of the ray.
        # e.g. The intersection point is not on the edge.
        if t > 0 and t < l:
            # The vector value of 't'.
            q = Vector3(self.edges[edgeId].v0) + (dUnit * t)
            return (q - pointQ).length()
        
        else:
            return MAX


    def distanceToPlane(self, pointQ):
        """
        Calculates the shortest distance from 'pointQ' to the plane 
        formed by the three vertices of the triangle.
        
        'pointQ' could be nowhere near the defined triangle and still
        return a relative small number as it check's the distance to the
        infinite plane the triangle lies on.
        """
        # Project 'pointQ' onto the plane.
        return  pointQ * self.normal - self.d
    
    def intersectionPoint(self, pointQ, displacement):
        """
        Finds the intersection point of the line formed by the shortest
        distance from 'pointQ' to the plane of the triangle.
        
        presumes that 'distance' is of a valid value.
        """
        return pointQ + (-displacement * self.normal)
    
    def examinePoint(self, pointQ, threshold):
        """
        Checks if 'pointQ' is within the 'distance' threshold to the triangle.
        
        1. Compute the distance from 'pointQ' to the triangle.
        
        2. If distance <= to the threshold, check if the point is within the 
            boundaries of the triangle.
            
        3. If the point is not within the triangle, check its distance to
            the edges of the triangle to see if 'pointQ' is still within the threshold.
            
        """
        
        # ----- 1.0
        distance = self.distanceToPlane(pointQ)
        
        
        if abs(distance) <= threshold:
            # ----- 2.0 Calculate the intersection point onto the plane of the triangle.
            ip = self.intersectionPoint(pointQ, distance)
            
            # ----- 2.1 Calculate the barycentric coordinates of the intersection point.
            baryCord = self.barycentric(ip)
            
            # ----- 2.2 Analyze the barycentric coordinate.
            component = self.examineBaryCord(baryCord)
            
            # ----- 2.2.1 Barycentric coordinate is within the triangle.
            if component == 3:
                return True
            
            # ----- 2.2.2 Not within the triangle and closest to a vertex.
            if component == 4:
                return False
            
            # ----- 2.2.3 Not within the triangle and closest to edge 'n'.
            if component == 0 or component == 1 or component == 2:
                distance = self.distanceToEdge(component, pointQ)
                if distance <= threshold:
                    return True
                
        else:
            return False